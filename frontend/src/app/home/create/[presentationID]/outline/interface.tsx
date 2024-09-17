"use client";

import { Spinner, Spacer, Button, ScrollShadow } from "@nextui-org/react";
import { TopicCard } from "@/components/topic-card";
import { useRouter } from "next/navigation";
import { Icon } from "@iconify/react";
import { DragDropContext, Droppable, Draggable, DropResult } from "react-beautiful-dnd";
import { useState, useEffect } from "react";
import { retrieveSources } from "@/actions/get-all-sources";

interface InterfaceProps {
    includedTopics: any[];
    setIncludedTopics: any;
    excludedTopics: any[];
    setExcludedTopics: any;
    block: boolean;
    presentationID: string;
    redirectPath: string;
}

export default function Interface({
    includedTopics,
    setIncludedTopics,
    excludedTopics,
    setExcludedTopics,
    block,
    presentationID,
    redirectPath,
}: InterfaceProps) {

    const router = useRouter();
   
    const [allSources, setAllSources] = useState<any[]>([]);
    const [continueButtonLoading, setContinueButtonLoading] = useState(false);

      useEffect(() => {
        const updateSources = async () => {
          const sources = await retrieveSources(presentationID)
          sources && setAllSources(sources)
        }
     
        updateSources()
      }, [])

    const handleDragEnd = (result: DropResult) => {
        if (!result.destination) return;

        const source = result.source.droppableId;
        const destination = result.destination.droppableId;

        if (source === destination) {
            // Reorder within the same section
            const items = Array.from(source === "included" ? includedTopics : excludedTopics);
            const [reorderedItem] = items.splice(result.source.index, 1);
            items.splice(result.destination.index, 0, reorderedItem);

            if (source === "included") {
                setIncludedTopics(items);
            } else {
                setExcludedTopics(items);
            }
        } else {
            // Move between sections
            const sourceItems = Array.from(source === "included" ? includedTopics : excludedTopics);
            const [movedItem] = sourceItems.splice(result.source.index, 1);
            const destinationItems = Array.from(destination === "included" ? includedTopics : excludedTopics);
            destinationItems.splice(result.destination.index, 0, movedItem);

            if (source === "included") {
                setIncludedTopics(sourceItems);
                setExcludedTopics(destinationItems);
            } else {
                setExcludedTopics(sourceItems);
                setIncludedTopics(destinationItems);
            }
        }
    };

    return (
        <div className="flex flex-col h-full flex-auto">
            {/* Sticky title at top */}
            <div className="text-center p-1 translate-y-2">
                {/* Text and spinner side by side */}
                <div className="flex gap-2 align-middle justify-center ">
                    <p>{"List of Subtopics"}</p>
                </div>
            </div>
            {/* { JSON.stringify(includedTopics) + "and" + JSON.stringify(excludedTopics)} */}
            <ScrollShadow className="flex-auto" hideScrollBar size={80}>
                {
                    !includedTopics.length && !excludedTopics.length ? (
                        <>
                            <Spacer y={6} />
                            <div className="text-foreground/70 italic text-center">
                                Shiro will create a list of subtopics to include in your presentation.
                            </div>
                        </>
                    ) : (<>
                        <DragDropContext onDragEnd={handleDragEnd}>
                            <div className="flex flex-col gap-4">
                                <div>
                                    <h2 className="text-xl font-semibold mb-2">Included Subtopics</h2>
                                    <Droppable droppableId="included">
                                        {(provided) => (
                                            <div
                                                {...provided.droppableProps}
                                                ref={provided.innerRef}
                                                className={`${includedTopics.length
                                                    ? "flex flex-col gap-4 py-4"
                                                    : "flex flex-col items-center justify-center"
                                                    } min-h-[100px]`}
                                            >
                                                {includedTopics.length === 0 && (
                                                    <div className="text-foreground/70 italic">
                                                        Drag subtopics here to include them in the presentation.
                                                    </div>
                                                )}
                                                {includedTopics.map((topic: any, index) => (
                                                    <Draggable key={topic.topic_id} draggableId={topic.topic_id} index={index}>
                                                        {(provided) => (
                                                            <TopicCard
                                                                topic={topic}
                                                                provided={provided}
                                                                included={true}
                                                                allSources={allSources}
                                                            />
                                                        )}
                                                    </Draggable>
                                                ))}
                                                {provided.placeholder}
                                            </div>
                                        )}
                                    </Droppable>
                                </div>

                                <div>
                                    <h2 className="text-xl font-semibold mb-2">Excluded Subtopics</h2>
                                    <Droppable droppableId="excluded">
                                        {(provided) => (
                                            <div
                                                {...provided.droppableProps}
                                                ref={provided.innerRef}
                                                className={`${excludedTopics.length
                                                    ? "flex flex-col gap-4 py-4"
                                                    : "flex flex-col items-center justify-center"
                                                    } min-h-[100px]`}
                                            >
                                                {excludedTopics.length === 0 && (
                                                    <div className="text-foreground/70 italic">
                                                        Drag subtopics here to exclude them from the presentation.
                                                    </div>
                                                )}
                                                {excludedTopics.map((topic: any, index) => (
                                                    <Draggable key={topic.topic_id} draggableId={topic.topic_id} index={index}>
                                                        {(provided) => (
                                                            <TopicCard
                                                                topic={topic}
                                                                provided={provided}
                                                                included={false}
                                                                allSources={allSources}
                                                            />
                                                        )}
                                                    </Draggable>
                                                ))}
                                                {provided.placeholder}
                                            </div>
                                        )}
                                    </Droppable>
                                </div>
                            </div>
                        </DragDropContext>
                    </>
                    )
                }

                <Spacer y={6} />
            </ScrollShadow>

            <Button
                color="primary"
                className="min-h-[64px] flex flex-row rounded-b-none text-base"
                isDisabled={!includedTopics.length || block}
                onClick={() => {
                    includedTopics.length && !block && setContinueButtonLoading(true);
                    includedTopics.length && !block && router.push(redirectPath);
                }}
                isLoading={continueButtonLoading}
            >
                <span>Proceed to the next step</span>
                <Icon icon="tabler:arrow-narrow-right" width={30} />
            </Button>
        </div>
    );
}