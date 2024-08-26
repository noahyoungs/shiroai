"use client";

import { useEffect } from "react";

const fetchSignedCookies = async (presentationID: string) => {
  try {
    const response = await fetch(`/api/images/cookie/${presentationID}`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch signed cookies");
    }

    console.log("Signed cookies fetched successfully");
  } catch (error) {
    console.error("Error fetching signed cookies:", error);
  }
};

export default function Layout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { presentationID: string };
}) {
  useEffect(() => {
    fetchSignedCookies(params.presentationID);
  }, []);

  return children;
}
