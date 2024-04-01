"use client"
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell, Link, Tab } from "@nextui-org/react";
import { ReactNode } from "react";

type PresentationProps = {
  presentations?: {
    id: string;
    topic?: string;
    status?: string;
    time_updated: number;
  }[];
  bottomContent: ReactNode;
};

function PresentationTable({ presentations, bottomContent }: PresentationProps) {

  return (
    <Table
      aria-label="Example table with dynamic content"
      bottomContent={bottomContent}
      className="p-5"
    >
      <TableHeader>
        <TableColumn>Description</TableColumn>
        <TableColumn>Status</TableColumn>
        <TableColumn>Updated Time</TableColumn>
        {/* <TableColumn>Actions</TableColumn> */}
      </TableHeader>
      <TableBody>
        {presentations && presentations.length > 0 ? (
          presentations.map((presentation) => (
            <TableRow key={presentation.id}>
              <TableCell>{presentation.topic || presentation.id}</TableCell>
              <TableCell>{presentation.status || "Unknown"}</TableCell>
              <TableCell>{formatTimestamp(presentation.time_updated)}</TableCell>
              {/* <TableCell>
                <Link
                  >
                  Go
                </Link>
              </TableCell> */}
            </TableRow>
          ))
        ) : (
          <TableRow>
            <TableCell>No presentations found</TableCell>
            <TableCell>{null}</TableCell>
            <TableCell>{null}</TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}

// Helper function to format the timestamp
function formatTimestamp(timestamp: number): string {

    const date = new Date(timestamp * 1000);
    
    return date.toLocaleString();
    
    }

export default PresentationTable;