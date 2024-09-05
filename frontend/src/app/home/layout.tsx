import type { ReactNode } from 'react';
import { redirect } from "next/navigation";
import { auth } from "@/auth"
import SideBar from "@/components/sidebar-with-gradient-background/sidebar";
import SidebarList from "@/components/sidebar-with-gradient-background/sidebar-list";

type LayoutProps = {
    children: ReactNode;
};

async function Layout({ children }: LayoutProps) {
    const session = await auth();
    if (!session || !session.user) {
        redirect("/api/auth/signin");
        return <div>You must be signed in to view this page.</div>;
    }

    return (
        <section style={{ height: '100vh' }}>
            <SideBar
                list={<SidebarList />}
            >
                {children}
            </SideBar>

        </section>
    );
}

export default Layout;