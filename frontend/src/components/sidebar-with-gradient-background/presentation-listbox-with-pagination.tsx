"use client"
import { useState, useEffect, useRef } from "react";
import PresentationListbox from "@/components/presentation-listbox";
import { Spinner } from "@nextui-org/react";

const PresentationListboxWithPagination = () => {
  const [presentations, setPresentations] = useState<Array<{presentation_id: string, topic: string, gsi1sk: string, status: string}>>([]);
  const [loading, setLoading] = useState(false);
  const [lastFetchedGSI1SK, setLastFetchedGSI1SK] = useState<string | null>(null);
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
        body: JSON.stringify({ lastFetchedGSI1SK }),
      });
      const data = await response.json();
      if (response.ok) {
        setPresentations(prev => [...prev, ...data.presentations]);
        setLastFetchedGSI1SK(data.lastFetchedGSI1SK);
        setHasMore(!!data.lastFetchedGSI1SK);
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
  }, [loaderRef.current, loading, hasMore]);

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