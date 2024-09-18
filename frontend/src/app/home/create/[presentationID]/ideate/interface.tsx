// interface.tsx
"use client"
import { Textarea, Button, Spacer, ScrollShadow, Tooltip } from "@nextui-org/react";
import { useRouter } from 'next/navigation';
import { Icon } from "@iconify/react";
import { useState } from "react";


interface InterfaceProps {
    topic: string;
    audience: string;
    goal: string;
    setTopic: (topic: string) => void;
    setAudience: (targetAudience: string) => void;
    setGoal: (goal: string) => void;
    block: boolean;
    redirectPath: string;
    presentationID: string;
}

export default function Interface({ topic, audience, goal, setTopic, setAudience, setGoal, block, redirectPath }: InterfaceProps) {
    const router = useRouter();
    const [continueButtonLoading, setContinueButtonLoading] = useState(false);
    return (
        <div className="flex flex-col h-full flex-auto">
            {/* Sticky title at top */}
            <div className="text-center p-1 translate-y-2">
                {/* Text and spinner side by side */}
                <div className="flex gap-2 align-middle justify-center">
                    <p>{"Your Presentation Idea"}</p>
                    {/* {(loading) &&
                <Spinner size="sm" className="p-0 m-0" />
              } */}
                </div>
            </div>
            <ScrollShadow
                className="flex-auto"
                hideScrollBar
                size={80}
            >
                {
                    (!topic && !audience && !goal) && (
                        <>
                            <Spacer y={6} />
                            <div className="text-foreground/70 italic">
                                Shiro will help you develop your presentation idea. <br />
                                To begin, ask Shiro to help you brainstorm, or enter your own ideas below.
                            </div>
                        </>
                    )
                }


                <Spacer y={6} />
                <h3>Presentation Topic</h3>
                <Textarea
                    aria-label="Topic"
                    placeholder="Enter your description"
                    className=""
                    value={topic}
                    onValueChange={setTopic}
                    isDisabled={block}

                />
                <Spacer y={6} />
                <h3>Target Audience</h3>
                <Textarea
                    aria-label="Target Audience"
                    placeholder="Enter your description"
                    className=""
                    value={audience}
                    onValueChange={setAudience}
                    isDisabled={block}
                />
                <Spacer y={6} />
                <h3>Presentation Goal</h3>
                <Textarea
                    aria-label="Goal"
                    placeholder="Enter your description"
                    className=""
                    value={goal}
                    onValueChange={setGoal}
                    isDisabled={block}
                />

            </ScrollShadow>
            <Button
                color="primary"
                className="min-h-[64px] flex flex-row rounded-b-none text-base"
                onClick={() => {
                    !block && topic && audience && goal && setContinueButtonLoading(true);
                    !block && topic && audience && goal && router.push(redirectPath);
                }}
                isDisabled={block || !topic || !audience || !goal}
                isLoading={continueButtonLoading}
            >
                <span>Proceed to the next step</span>
                <Icon icon="tabler:arrow-narrow-right" width={30} />
            </Button>
        </div>
    );
}