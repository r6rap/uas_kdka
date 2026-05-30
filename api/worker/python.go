package worker

import (
	"fmt"
	"os/exec"
	"github.com/r6rap/uas_kdka/api/job"
)

func RunMosaic(jobID, targetPath, category, outputPath string) {
	job.Global.Update(jobID, job.StatusProcessing, "", "")

	cmd := exec.Command("python", "main.py", targetPath, category, outputPath)

	output, err := cmd.CombinedOutput()
	if err != nil {
		job.Global.Update(jobID, job.StatusFailed, "", fmt.Sprintf("%v: %s", err, string(output)))
		return
	}

	job.Global.Update(jobID, job.StatusDone, outputPath, "")
}