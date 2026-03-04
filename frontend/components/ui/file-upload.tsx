import * as React from "react"
import { Upload, X } from "lucide-react"
import { Button } from "./button"
import { cn } from "@/lib/utils"

interface FileUploadProps {
  onFileSelect: (files: FileList | null) => void
  accept?: string
  multiple?: boolean
  maxSize?: number // in MB
  className?: string
  disabled?: boolean
  children?: React.ReactNode
}

export function FileUpload({
  onFileSelect,
  accept = "*",
  multiple = false,
  maxSize = 10,
  className = "",
  disabled = false,
  children,
}: FileUploadProps) {
  const [dragActive, setDragActive] = React.useState(false)
  const [selectedFiles, setSelectedFiles] = React.useState<File[]>([])
  const inputRef = React.useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleFiles = (files: FileList) => {
    const validFiles: File[] = []
    const maxSizeBytes = maxSize * 1024 * 1024

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      if (file.size <= maxSizeBytes) {
        validFiles.push(file)
      } else {
        console.warn(`File ${file.name} is too large. Max size: ${maxSize}MB`)
      }
    }

    if (validFiles.length > 0) {
      setSelectedFiles(validFiles)
      onFileSelect(validFiles.length > 0 ? { 0: validFiles[0], length: validFiles.length } as any : null)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files)
    }
  }

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(newFiles)
    onFileSelect(newFiles.length > 0 ? { 0: newFiles[0], length: newFiles.length } as any : null)
  }

  const onButtonClick = () => {
    inputRef.current?.click()
  }

  return (
    <div className={className}>
      <div
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center transition-colors",
          dragActive ? "border-primary bg-primary/5" : "border-gray-300",
          disabled && "opacity-50 cursor-not-allowed"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleChange}
          disabled={disabled}
          className="hidden"
        />

        {children ? (
          <div onClick={onButtonClick} className="cursor-pointer">
            {children}
          </div>
        ) : (
          <div onClick={onButtonClick} className="cursor-pointer">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-4">
              <p className="text-sm text-gray-600">
                Drag and drop files here, or{" "}
                <span className="text-primary font-medium">browse</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Max file size: {maxSize}MB
              </p>
            </div>
          </div>
        )}
      </div>

      {selectedFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          {selectedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 bg-gray-50 rounded-md"
            >
              <div className="flex items-center space-x-2">
                <div className="text-sm text-gray-900">{file.name}</div>
                <div className="text-xs text-gray-500">
                  ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeFile(index)}
                className="h-6 w-6 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}