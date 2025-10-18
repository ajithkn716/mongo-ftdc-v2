// main.go
package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "io/ioutil"
    "log"
    "os"
    "path/filepath"

    "ftdc/decoder" // Adjust the import path based on your project structure
)

func main() {
    // Command-line flags for input/output files and progress info
    inputFile := flag.String("input", "", "Path to the input file")
    outputFile := flag.String("output", "", "Path to the output file")
    fileIdx := flag.Int("idx", 0, "Current file index")
    fileTotal := flag.Int("total", 0, "Total number of files")
    flag.Parse()

    if *inputFile == "" || *outputFile == "" {
        log.Fatal("Input and output files must be specified")
    }

    // Prefix for log messages
    prefix := fmt.Sprintf("[%d/%d]", *fileIdx, *fileTotal)

    // Ensure input file path is absolute
    absInputPath, err := filepath.Abs(*inputFile)
    if err != nil {
        log.Fatalf("%s Failed to get absolute path of input file: %v", prefix, err)
    }

    // Ensure output file path is absolute
    absOutputPath, err := filepath.Abs(*outputFile)
    if err != nil {
        log.Fatalf("%s Failed to get absolute path of output file: %v", prefix, err)
    }

    // Read the input file
    // fmt.Printf("%s Reading MongoDB FTDC file: %s\n", prefix, absInputPath)
    data, err := ioutil.ReadFile(absInputPath)
    if err != nil {
        log.Fatalf("%s Failed to read input file: %v", prefix, err)
    }

    // Decode the metrics
    fmt.Printf("%s Decoding MongoDB FTDC data...\n", prefix)
    metrics := decoder.NewMetrics()
    err = metrics.ReadAllMetrics(&data)
    if err != nil {
        log.Fatalf("%s Failed to decode metrics: %v", prefix, err)
    }

    // Convert the metrics to JSON
    // fmt.Printf("%s Converting metrics to JSON...\n", prefix)
    jsonData, err := json.MarshalIndent(metrics, "", "  ")
    if err != nil {
        log.Fatalf("%s Failed to marshal metrics to JSON: %v", prefix, err)
    }

    // Ensure the output directory exists
    outputDir := filepath.Dir(absOutputPath)
    if _, err := os.Stat(outputDir); os.IsNotExist(err) {
        os.MkdirAll(outputDir, os.ModePerm)
        // fmt.Printf("%s Created output directory: %s\n", prefix, outputDir)
    }

    // Write the JSON data to the output file
    // fmt.Printf("%s Writing JSON output to %s\n", prefix, absOutputPath)
    err = ioutil.WriteFile(absOutputPath, jsonData, 0644)
    if err != nil {
        log.Fatalf("%s Failed to write output file: %v", prefix, err)
    }

    // fmt.Printf("%s Successfully wrote metrics to JSON file.\n", prefix)
}
