# Phase 6 Validation Tests

## Overview

This directory contains comprehensive validation tests for Phase 6, which includes:
- Auto vs Manual Mode system
- UI integration
- Explainability Layer (XAI)

## Test Files

### 1. `validation_test.go`
Go tests for backend validation:
- `TestAutoModeValidation`: Tests Auto Mode functionality
- `TestManualModeValidation`: Tests Manual Mode functionality
- `TestExplanationHumanReadable`: Validates explanations are human-readable
- `TestLoggingValidation`: Tests logging functionality
- `TestUIDynamicUpdates`: Tests UI data structure
- `TestFullSystemIntegration`: Tests full system integration

### 2. `ui_validation_test.js`
JavaScript tests for UI validation:
- `testAutoModeUI()`: Tests Auto Mode UI structure
- `testManualModeUI()`: Tests Manual Mode UI structure
- `testExplanationFormat()`: Tests explanation format
- `testUIDynamicUpdates()`: Tests UI dynamic updates

### 3. `validation_report.go`
Generates comprehensive validation reports with:
- Test results
- Component validation status
- Recommendations
- JSON and human-readable formats

### 4. `run_validation.sh`
Shell script to run all validation tests

## Running Tests

### Go Tests

```bash
cd tests/phase6
go test -v
```

Run specific test:
```bash
go test -v -run TestAutoModeValidation
```

### JavaScript Tests

```bash
node tests/phase6/ui_validation_test.js
```

### Full Validation

```bash
chmod +x tests/phase6/run_validation.sh
./tests/phase6/run_validation.sh
```

## Validation Checklist

### ✅ Auto Mode
- [x] Triggers actions without user input
- [x] Displays explanation after execution
- [x] Confidence level >= 0.9 (95%)
- [x] Explanation contains reasoning chain

### ✅ Manual Mode
- [x] Waits for user input
- [x] Shows available actions
- [x] Displays full reasoning after selection
- [x] Confidence level 0.8-0.9 (85%)
- [x] Options have risk/impact/cost information

### ✅ Explanations
- [x] Human-readable format
- [x] Step-by-step reasoning chain
- [x] Contains required fields (Agent, Action, Reasoning)
- [x] Valid JSON format
- [x] Alternative actions listed

### ✅ Logging
- [x] All agents send reliable logs
- [x] Logs contain detailed explanations
- [x] ELK Stack integration (if configured)
- [x] File fallback logging
- [x] All required fields present

### ✅ UI
- [x] Updates dynamically based on mode
- [x] Auto Mode displays executed actions
- [x] Manual Mode displays options
- [x] JSON serialization works
- [x] Mode field present in data

## Expected Results

All tests should pass with:
- ✅ Auto Mode: Action executed automatically, explanation displayed
- ✅ Manual Mode: User input requested, options shown, full reasoning after selection
- ✅ Explanations: Human-readable with step-by-step reasoning
- ✅ Logging: All explanations logged with required fields
- ✅ UI: Dynamic updates based on mode

## Troubleshooting

### Go Tests Fail
- Ensure Go is installed: `go version`
- Check imports are correct
- Verify core package is accessible

### JavaScript Tests Fail
- Ensure Node.js is installed: `node --version`
- Check file paths are correct
- Verify mock data structure

### Logging Tests Fail
- Check log directory permissions
- Verify ELK Stack URL (if configured)
- Check file system write permissions

## Report Generation

Generate validation report:
```go
package main

import (
    "fmt"
    "github.com/ai-driven-self-healing-cloud/tests/phase6"
)

func main() {
    report, err := phase6.GenerateValidationReport()
    if err != nil {
        panic(err)
    }
    
    fmt.Println(report.ToHumanReadable())
    report.SaveReport("validation_report.json")
}
```

## Next Steps

After validation:
1. Fix any failing tests
2. Review recommendations in report
3. Integrate with CI/CD pipeline
4. Set up automated validation
5. Monitor validation results

