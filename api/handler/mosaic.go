package handler

import (
	"fmt"
	"net/http"
	"path/filepath"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/r6rap/uas_kdka/api/job"
	"github.com/r6rap/uas_kdka/api/worker"
)

func PostMosaic(c *gin.Context) {
	category := c.PostForm("category")
	if category == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "category is required"})
		return
	}

	valid := map[string]bool{"building": true, "cloud": true, "nature": true, "vehicle": true}
	if !valid[category] {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("invalid category: %s", category)})
		return
	}


	file, err := c.FormFile("image")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "image file is required"})
		return
	}

	
	jobID := fmt.Sprintf("%d", time.Now().UnixNano())
	uploadPath := filepath.Join("uploads", jobID+"_"+file.Filename)
	if err := c.SaveUploadedFile(file, uploadPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to save uploaded file"})
		return
	}


	outputPath := filepath.Join("outputs", jobID+".jpg")
	job.Global.Create(jobID)

	go worker.RunMosaic(jobID, uploadPath, category, outputPath)

	c.JSON(http.StatusAccepted, gin.H{
		"job_id": jobID,
		"status": "pending",
	})
}