import type { ReactNode } from 'react';
import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";
import NavBar from "@/components/navbar/navbar";


type LayoutProps = {
    children: ReactNode;
};

async function Layout({ children }: LayoutProps) {
    const session = await getServerSession();
    if (!session || !session.user) {
        redirect("/api/auth/signin");
        return <div>You must be signed in to view this page.</div>;
    }

    return (
        <section style={{height: '100vh'}}>
            <NavBar />
            {children}
        </section>
    );
}

export default Layout;