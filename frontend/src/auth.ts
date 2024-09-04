import NextAuth from "next-auth";
import Cognito from "next-auth/providers/cognito"

export const { auth, handlers, signIn, signOut } = NextAuth({
  secret: process.env.NEXTAUTH_SECRET,
  providers: [
    Cognito({checks: ["nonce"]})
  ],
  pages: {
    signIn: "/auth/signin",
  },
  cookies: {
    sessionToken: {
      name: `__Secure-next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: "none",
        path: "/",
        secure: true,
      },
    },
  },
  callbacks: {
    async session({ session, token, user }) {
      session.user.id = token.sub!;      
      return session
    }
  }
});
