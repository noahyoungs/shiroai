"use client";

import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { Button, Tooltip, Badge, Card, CardBody } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { getIcon } from "@/utils/get-file-icon";

import { cn } from "@/utils/cn";

import PromptInput from "./prompt-input";

export default function Component({
  socket,
  block,
  setBlockSend,
  sources,
  presentationID,
  refreshSources,
  onHeightChange,
}: {
  socket: any,
  block: boolean,
  setBlockSend: (block: boolean) => void,
  sources: any,
  presentationID: string,
  refreshSources: () => void,
  onHeightChange?: (height: number, meta: { rowHeight: number }) => void,
}) {
  // const [isRegenerating, setIsRegenerating] = useState<boolean>(false);
  const [prompt, setPrompt] = useState<string>("");
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  // const onRegenerate = () => {
  //   setIsRegenerating(true);
  //   setTimeout(() => {
  //     setIsRegenerating(false);
  //   }, 1000);
  // };

  const sendMessage = async () => {
    if (files.length > 0) {
      let success = await upload();
      // if upload is successful, send message
      if (success) {
        // template message for when theres no message
        let promptToSend = prompt.trim() || `I uploaded ${files.length} file${files.length > 1 ? 's' : ''}: ${files.map(file => file.name).join(', ')}`
        setPrompt("");
        socket.emit("message", promptToSend);
        setBlockSend(true);
      }
    } else {
      // if no files
      console.log("Sending message: ", prompt)
      if (prompt.trim() !== "" && socket) {
        socket.emit("message", prompt);
        setPrompt("");
        setBlockSend(true);
      }
    }
  };

  const upload = async () => {
    let acceptedFiles = files;
    if (acceptedFiles.length === 0) {
      alert('Please select files to upload.');
      return false;
    }

    // alert and return if any file in acceptedFiles has the same name as a file in sources
    const fileNames = acceptedFiles.map(file => file.name);
    const sourceFileNames = sources.map((source: { s3_filepath?: string; }) => source.s3_filepath);
    const duplicateFileNames = fileNames.filter(fileName => sourceFileNames.includes(fileName));
    if (duplicateFileNames.length > 0) {
      alert(`The following files already exist in the source list: ${duplicateFileNames.join(', ')}. Please rename before uploading.`);
      return false;
    }

    // alert and return if two or more files in acceptedFiles have the same name
    const uniqueFileNames = new Set(fileNames);
    if (uniqueFileNames.size !== fileNames.length) {
      alert('One or more of the selected files have the same name. Please rename before uploading.');
      return false;
    }

    setFiles(acceptedFiles);
    setUploading(true);

    for (const file of acceptedFiles) {
      // Upload file to S3
      const response = await fetch(
        process.env.NEXT_PUBLIC_BASE_URL + '/api/upload',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ filename: file.name, contentType: file.type, presentationID }),
        }
      );

      if (response.ok) {
        const { url, fields } = await response.json();
        const formData = new FormData();
        Object.entries(fields).forEach(([key, value]) => {
          formData.append(key, value as string);
        });
        formData.append('file', file);

        const uploadResponse = await fetch(url, {
          method: 'POST',
          body: formData,
        });

        if (!uploadResponse.ok) {
          console.error('S3 Upload Error:', uploadResponse);
          try {
            const errorBody = await uploadResponse.text();
            console.error('Error Body:', errorBody);
          } catch (err) {
            console.error('Failed to parse error body:', err);
          }
          alert(`Upload failed for file: ${file.name}`);
          return false;
        }
      } else {
        alert(`Failed to get pre-signed URL for file: ${file.name}`);
        return false;
      }
    }

    // Clear the files state
    setFiles([]);
    setUploading(false);
    refreshSources();

    return true;
  };

  const onDrop = async (acceptedFiles: File[]) => {
    // append to files
    setFiles(oldFiles => [...oldFiles, ...acceptedFiles]);
  }


  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop: onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/rtf': ['.rtf'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
    },
    disabled: uploading,
    noClick: true,
  });

  const deleteFile = (index: number) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);
  }

  return (
    <div {...getRootProps()} className="flex w-full flex-col gap-4 flex-grow">
      <form className="flex w-full flex-col items-start rounded-t-xl bg-default-100 transition-colors hover:bg-default-200/70 h-full">
        <div className={cn("flex w-full items-center justify-start px-4 gap-4 h-full", files.length > 0 && "mt-3")}>
          {files.length > 0 && (
            files.map((file, index) => (
              <Badge
                content={<Icon icon="tabler:x" width={17} className="flex-none p-0 m-0" />}
                color="danger"
                shape="rectangle"
                showOutline={false}
                isOneChar
                onClick={deleteFile.bind(null, index)}
              >
                <Tooltip content={file.name} size="lg" offset={20} className="px-2 py-1" closeDelay={0} placement="top-start">
                  <Card key={index} className="bg-default/40">
                    <CardBody className="flex flex-row gap-2 items-center">
                      <Icon icon={getIcon(file.name) || 'tabler:file-unknown'} width={25} className="text-default-600" />
                    </CardBody>
                  </Card>
                </Tooltip>
              </Badge>
            )))}
          <div className="flex-grow"></div>
          {
            uploading && (
              <div className="text-default-600">
                <svg xmlns="http://www.w3.org/2000/svg" width={48} height={48} viewBox="0 0 24 24"><g fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth={1.25}><path strokeDasharray="2 4" strokeDashoffset={6} d="M12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3"><animate attributeName="stroke-dashoffset" dur="0.6s" repeatCount="indefinite" values="6;0"></animate></path><path strokeDasharray={30} strokeDashoffset={30} d="M12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21"><animate fill="freeze" attributeName="stroke-dashoffset" begin="0.1s" dur="0.3s" values="30;0"></animate></path><path strokeDasharray={10} strokeDashoffset={10} d="M12 16v-7.5"><animate fill="freeze" attributeName="stroke-dashoffset" begin="0.5s" dur="0.2s" values="10;0"></animate></path><path strokeDasharray={6} strokeDashoffset={6} d="M12 8.5l3.5 3.5M12 8.5l-3.5 3.5"><animate fill="freeze" attributeName="stroke-dashoffset" begin="0.7s" dur="0.2s" values="6;0"></animate></path></g></svg>
              </div>
            )
          }
        </div>
        <PromptInput
          classNames={{
            inputWrapper: "!bg-transparent shadow-none h-full flex-grow p-4",
            innerWrapper: "relative h-full",
            input: "pr-10 text-medium h-full",
          }}
          endContent={
            <div className="flex items-end gap-1.5">
              <Tooltip
                showArrow
                placement="top"
                color="default"
                content="Attach files"
              >
                <Button
                  size="sm"
                  isIconOnly
                  variant="solid"
                  radius="lg"
                  onClick={open}
                >
                  <Icon className="text-default-500" icon="tabler:paperclip" width={18} />
                </Button>
              </Tooltip>
              <Tooltip
                showArrow
                placement="top-end"
                color={block ? "warning" : "default"}
                content={block ? 'Please wait until the assistant replies' : 'Send message'}
              >
                <Button
                  isIconOnly
                  color={!(prompt || (files.length > 0)) || block ? "default" : "primary"}
                  radius="lg"
                  size="sm"
                  variant="solid"
                >
                  <Icon
                    className={cn(
                      "[&>path]:stroke-[2px]",
                      !(prompt || (files.length > 0)) || block ? "text-default-600" : "text-primary-foreground",
                    )}
                    icon="tabler:arrow-narrow-up"
                    // icon={uploading ? "line-md:uploading-loop" : "tabler:arrow-narrow-up"}
                    // icon="line-md:uploading-loop"
                    width={20}
                    onClick={() => { if (!block) sendMessage() }}
                  />
                </Button>
              </Tooltip>
            </div>
          }
          radius="lg"
          value={prompt}
          variant="flat"
          onValueChange={setPrompt}
          onSendMessage={() => { if (!block) sendMessage() }}
          placeholder={"Message Shiro or drag and drop files here..."}
          onHeightChange={onHeightChange}
        />
        <div className="flex w-full flex-wrap items-center justify-between gap-2 px-4">
          <div className="flex flex-wrap gap-3">
            <input {...getInputProps()}></input>
          </div>
          {/* <p className="py-1 text-tiny text-default-400">{prompt.length}/2000</p> */}
        </div>
      </form>
    </div>
  );
}
