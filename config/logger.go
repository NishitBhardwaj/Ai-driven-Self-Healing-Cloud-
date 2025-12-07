package config

import (
	"os"

	"github.com/sirupsen/logrus"
)

var globalLogger *logrus.Logger

// InitLogger initializes the global logger instance
func InitLogger() *logrus.Logger {
	logger := logrus.New()
	logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
		ForceColors:   true,
	})

	// Set log level based on config
	level := GetConfig().LogLevel
	switch level {
	case "debug":
		logger.SetLevel(logrus.DebugLevel)
	case "info":
		logger.SetLevel(logrus.InfoLevel)
	case "warn":
		logger.SetLevel(logrus.WarnLevel)
	case "error":
		logger.SetLevel(logrus.ErrorLevel)
	default:
		logger.SetLevel(logrus.InfoLevel)
	}

	// Set output to stdout
	logger.SetOutput(os.Stdout)

	globalLogger = logger
	return logger
}

// GetLogger returns the global logger instance
func GetLogger() *logrus.Logger {
	if globalLogger == nil {
		return InitLogger()
	}
	return globalLogger
}

// LogBoot logs a boot sequence message
func LogBoot(message string) {
	GetLogger().WithField("component", "boot").Info(message)
}

