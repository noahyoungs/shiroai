// route.ts
import NextAuth from 'next-auth';
import CognitoProvider from "next-auth/providers/cognito";

export const authOptions = {
    secret: process.env.NEXTAUTH_SECRET,
    providers: [
        CognitoProvider({
            clientId: process.env.COGNITO_CLIENT_ID ?? "",
            clientSecret: process.env.COGNITO_CLIENT_SECRET ?? "",
            issuer: process.env.COGNITO_ISSUER,
            checks: 'nonce',
            profile(profile) {
                return {
                  id: profile.sub,
                  name: profile.name,
                  email: profile.email,
                  image: profile.picture,
                }
          }})
    ],
    pages: {
        signIn: '/auth/signin',
    },
}
const handler = NextAuth(authOptions);
export { handler as GET, handler as POST};