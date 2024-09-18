"use client"
import { useState, useEffect, useRef } from "react";
import PresentationListbox from "@/components/presentation-listbox";
import { Spinner } from "@nextui-org/react";
import { AttributeValue } from "@aws-sdk/client-dynamodb";

interface Presentation {
  presentation_id: string;
  topic: string;
  status: string;
}

const PresentationListboxWithPagination = () => {
  const [presentations, setPresentations] = useState<Presentation[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastEvaluatedKey, setLastEvaluatedKey] = useState<Record<string, AttributeValue> | undefined>(undefined);
  const [hasMore, setHasMore] = useState(true);
  const loaderRef = useRef(null);

  const loadPresentations = async () => {
    if (loading || !hasMore) return;
    setLoading(true);
    try {
      const response = await fetch('/api/get_presentations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lastEvaluatedKey }),
      });
      const data = await response.json();
      if (response.ok) {
        setPresentations(prev => [...prev, ...data.presentations]);
        setLastEvaluatedKey(data.lastEvaluatedKey);
        setHasMore(!!data.lastEvaluatedKey);
      } else {
        console.error("Error loading presentations:", data.message);
        setHasMore(false);
      }
    } catch (error) {
      console.error("Error loading presentations:", error);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPresentations();
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading && hasMore) {
          loadPresentations();
        }
      },
      {
        rootMargin: '0px 0px 100px 0px',
        threshold: 0.1,
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
  }, [loading, hasMore]);

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