package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
)

var availableCategories = []string{"building", "cloud", "nature", "vehicle"}

func GetCategories(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"categories": availableCategories,
	})
}