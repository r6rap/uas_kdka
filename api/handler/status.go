package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/r6rap/uas_kdka/api/job"
)

func GetStatus(c *gin.Context) {
	id := c.Param("id")

	j, ok := job.Global.Get(id)
	if !ok {
		c.JSON(http.StatusNotFound, gin.H{"error": "job not found"})
		return
	}

	if j.Status != job.StatusDone {
		c.JSON(http.StatusOK, gin.H{
			"job_id": j.ID,
			"status": j.Status,
			"error":  j.Error,
		})
		return
	}

	c.File(j.OutputPath)
}