# Define the path to the codebase directory
$path = "./"

# Define the file extensions to include in the line count
$fileExtensions = @("*.cs", "*.py", "*.js", "*.html", "*.css")

# Initialize a counter for the total lines
$totalLines = 0

# Function to count lines in a file
function Get-LineCount {
    param (
        [string]$filePath
    )
    $lineCount = (Get-Content $filePath).Length
    return $lineCount
}

# Loop through each file extension and count the lines
foreach ($extension in $fileExtensions) {
    $files = Get-ChildItem -Recurse -File -Exclude "docs\*" | Where-Object { $_.FullName -notlike "*\docs\*" }
    foreach ($file in $files) {
        $totalLines += Get-LineCount -filePath $file.FullName
    }
}

# Output the total line count
Write-Output "Total lines of code: $totalLines"
