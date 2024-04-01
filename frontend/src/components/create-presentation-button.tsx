import React from "react";
import ActionCard from "@/components/action-card";
import CreatePresentation from "@/actions/create-presentation";


export default async function CreatePresentationButton(): Promise<React.ReactElement> {

    return (
        <ActionCard
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio."
            icon="solar:document-medicine-linear"
            title="Create a new presentation"
            className="border-2"
            color="primary"
            action={CreatePresentation}
        />
    )
}
