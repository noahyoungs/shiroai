"use client"
import { Icon } from "@iconify/react";
import React from "react";
import Markdown from 'react-markdown'
import { Card, Link, Image, CardHeader, CardBody, Divider, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, useDisclosure, Chip, Spacer, Progress, Accordion, AccordionItem } from "@nextui-org/react";
import { cn } from "@/utils/cn";
import { getIcon } from "@/utils/get-file-icon";
import { SearchResultItem } from "@/components/search-result-item";

interface TopicCardProps {
    topic: any;
    // onDelete: () => void;
    provided: any;
    included: boolean;
    allSources: any[];
}

export const TopicCard: React.FC<TopicCardProps> = ({ topic, provided, included, allSources }) => {
    const { isOpen, onOpen, onOpenChange } = useDisclosure();
    return (
        <>
            <div
                className={cn("rounded-xl flex flex-col bg-content2 max-w-full overflow-hidden p-4 hover:bg-content3", !included && 'opacity-50')}
                ref={provided.innerRef}
                {...provided.draggableProps}
                {...provided.dragHandleProps}
                onClick={onOpen}
                onPress={onOpen}
            >
                <div className="flex justify-left items-center">
                    {/* <div className="text-foreground/70 relative" >
                        <Icon icon="tabler:grip-vertical" width="30" height="30" />
                    </div> */}
                    <h3 className="text-lg mb-0 ml-2">{topic.name}</h3>
                    {/* <Icon
                    icon="tabler:trash-x"
                    width="27"
                    height="27"
                    className="text-danger/90 "
                    onClick={() => onDelete()}
                /> */}
                </div>
            </div>
            <Modal
                isOpen={isOpen}
                onOpenChange={onOpenChange}
                closeButton={
                    <Icon icon="tabler:x" width={40} height={40} />
                }
                classNames={{
                    closeButton: "top-3 right-3 w-[40px] h-[40px] p-0.5",
                }}
                size="4xl"
                scrollBehavior="outside"
            >
                <ModalContent>
                    {(onClose) => (
                        <>
                            <ModalHeader className="text-3xl mr-5 mt-2 inline"><span className="font-normal inline">Subtopic: </span>{topic.name}</ModalHeader>
                            <ModalBody>
                                <h3 className="font-medium mb-0 text-xl">Keywords</h3>
                                <div className="flex flex-row flex-wrap gap-2">
                                    {
                                        topic.keywords.map((keyword: any, index: number) => (
                                            <Chip key={index} color="primary" variant="flat">
                                                {keyword}
                                            </Chip>
                                        ))
                                    }
                                </div>
                                <Spacer y={2} />
                                <h3 className="font-medium mb-0 text-xl">Subtopic Evaluation</h3>
                                <Accordion variant="splitted" className="gap-4">
                                    <AccordionItem
                                        key="1"
                                        aria-label="Accordion 1"
                                        title={
                                            <Progress
                                                value={Number(topic.relevance_rating)}
                                                maxValue={5}
                                                className=""
                                                label="Relevance to Presentation Topic"
                                                showValueLabel
                                                color={Number(topic.relevance_rating) < 3 ? "danger" : Number(topic.relevance_rating) < 4 ? "warning" : "success"}
                                            />
                                        }
                                        classNames={{
                                            heading: "mb-0 pb-0",
                                        }}
                                    >
                                        <p className="mb-4">{topic.relevance_reasoning}</p>
                                    </AccordionItem>
                                    <AccordionItem
                                        key="2"
                                        aria-label="Accordion 2"
                                        title={
                                            <Progress
                                                value={Number(topic.value_rating)}
                                                maxValue={5}
                                                className=""
                                                label="Content Value"
                                                showValueLabel
                                                color={Number(topic.value_rating) < 3 ? "danger" : Number(topic.value_rating) < 4 ? "warning" : "success"}
                                            />
                                        }
                                        classNames={{
                                            heading: "mb-0 pb-0",
                                        }}
                                    >
                                        <p className="mb-4">{topic.value_reasoning}</p>
                                    </AccordionItem>
                                </Accordion>
                                <h3 className="font-medium mb-0 text-xl">Source Excerpts</h3>
                                <div className="flex flex-col gap-4 p-2">
                                    {topic.excerpts.map((excerpt: any, index: number) => (
                                        <Card key={index} className="">
                                            <CardHeader className="p-4">
                                                {Array.isArray(allSources) && allSources.length > 0 ? (
                                                    allSources.find((source) => source.id === excerpt.source.id) ? (
                                                        (matchedSource: any) => (
                                                            matchedSource.type === "web" ? (
                                                                <SearchResultItem source={matchedSource.web_source} description={false} />
                                                            ) : (
                                                                <div className="flex flex-row items-center gap-3">
                                                                    <Icon icon={getIcon(matchedSource.name) || 'file-unknown'} width={32} className="text-default-600" />
                                                                    <p>{matchedSource.name}</p>
                                                                </div>
                                                            )
                                                        )
                                                    )(allSources.find((source) => source.id === excerpt.source.id)) : (
                                                        <div className="flex flex-col">
                                                            <p>No match</p>
                                                            <p>Excerpt ID {excerpt}</p>
                                                            <p>Source: </p>
                                                            {excerpt.source.includes("http") ? (
                                                                <Link href={excerpt.source} isExternal showAnchorIcon>
                                                                    {excerpt.source}
                                                                </Link>
                                                            ) : (
                                                                excerpt.source
                                                            )}
                                                        </div>
                                                    )
                                                ) : (
                                                    <div className="flex flex-col">
                                                        <p>Source: </p>
                                                        {excerpt.source.includes("http") ? (
                                                            <Link href={excerpt.source} isExternal showAnchorIcon>
                                                                {excerpt.source}
                                                            </Link>
                                                        ) : (
                                                            excerpt.source
                                                        )}
                                                    </div>
                                                )}
                                            </CardHeader>
                                            <Divider />
                                            <CardBody className="px-4">
                                                <Markdown className="source-markdown mb-0">
                                                    {excerpt.content}
                                                </Markdown>
                                            </CardBody>
                                        </Card>
                                    ))}
                                </div>
                            </ModalBody>
                            <ModalFooter>
                                {/* <Button color="danger" variant="light" onPress={onClose}>
                                    Close
                                </Button>
                                <Button color="primary" onPress={onClose}>
                                    Action
                                </Button> */}
                                {null}
                            </ModalFooter>
                        </>
                    )}
                </ModalContent>
            </Modal>
        </>
    );
};