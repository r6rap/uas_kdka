package job

import (
	"sync"
	"time"
)

type Status string

const (
	StatusPending    Status = "pending"
	StatusProcessing Status = "processing"
	StatusDone       Status = "done"
	StatusFailed     Status = "failed"
)

type Job struct {
	ID         string
	Status     Status
	OutputPath string
	Error      string
	CreatedAt  time.Time
}

type Store struct {
	mu   sync.RWMutex
	jobs map[string]*Job
}

var Global = &Store{
	jobs: make(map[string]*Job),
}

func (s *Store) Create(id string) *Job {
	job := &Job{
		ID:        id,
		Status:    StatusPending,
		CreatedAt: time.Now(),
	}
	s.mu.Lock()
	s.jobs[id] = job
	s.mu.Unlock()
	return job
}

func (s *Store) Get(id string) (*Job, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	job, ok := s.jobs[id]
	return job, ok
}

func (s *Store) Update(id string, status Status, outputPath string, errMsg string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if job, ok := s.jobs[id]; ok {
		job.Status = status
		job.OutputPath = outputPath
		job.Error = errMsg
	}
}