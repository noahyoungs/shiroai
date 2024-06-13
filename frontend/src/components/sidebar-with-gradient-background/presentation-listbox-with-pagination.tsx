"use client"
import { useState, useEffect, useRef } from "react";
import PresentationListbox from "@/components/presentation-listbox";
import {Spinner} from "@nextui-org/react";

interface Presentation {
  id: string;
  topic: string;
  status: string;
  time_updated: number;
  href: string;
}

interface PresentationsResponse {
  presentations: Presentation[];
  lastEvaluatedKey: any;
}

const PresentationListboxWithPagination = ({ initialPresentations, initialLastEvaluatedKey }) => {
    const [presentations, setPresentations] = useState<Presentation[]>(initialPresentations);
    const [lastEvaluatedKey, setLastEvaluatedKey] = useState(initialLastEvaluatedKey);
    const [loading, setLoading] = useState(false);
    const loaderRef = useRef(null);
  
    const loadMorePresentations = async () => {
      if (!lastEvaluatedKey || loading) return;
  
      setLoading(true);
      try {
        const response = await fetch("/api/get_presentations", {
          method: "POST",
          body: JSON.stringify({ lastEvaluatedKey }),
          headers: {
            "Content-Type": "application/json",
          },
        });
  
        if (!response.ok) {
          console.error(`Error: ${response.statusText}`);
          setLoading(false);
          return;
        }
  
        const responseText = await response.text();
        console.log("Response Text:", responseText);
        const data: PresentationsResponse = JSON.parse(responseText);
  
        setPresentations((prev) => [...prev, ...data.presentations]);
        setLastEvaluatedKey(data.lastEvaluatedKey);
      } catch (error) {
        console.error("Failed to load more presentations:", error);
      } finally {
        setLoading(false);
      }
    };
  
    useEffect(() => {
      const observer = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting) {
            loadMorePresentations();
          }
        },
        {
          threshold: 1.0,
        }
      );
  
      if (loaderRef.current) {
        observer.observe(loaderRef.current);
      }
  
      return () => {
        if (loaderRef.current) {
          observer.unobserve(loaderRef.current);
        }
      };
    }, [loaderRef.current, lastEvaluatedKey]);
  
    return (
      <>
        <PresentationListbox presentations={presentations} />
        <div ref={loaderRef} style={{ height: 20, backgroundColor: "transparent" }}>
          {loading && <div className="flex flex-row justify-center my-2"><Spinner size="sm" color="primary"/></div>}
        </div>
      </>
    );
  };
  
  export default PresentationListboxWithPagination;