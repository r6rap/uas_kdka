package main

import (
	"log"
	"github.com/gin-gonic/gin"
	"github.com/r6rap/uas_kdka/api/handler"
)

func main() {
	r := gin.Default()

	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	r.GET("/categories", handler.GetCategories)
	r.POST("/mosaic", handler.PostMosaic)
	r.GET("/status/:id", handler.GetStatus)

	log.Println("server running on :8080")
	r.Run(":8080")
}