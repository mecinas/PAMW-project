import React from 'react'
import { useAuth0 } from '@auth0/auth0-react';

const LoginButton = () => {
    const { loginWithRedirect, isAuthenticated } = useAuth0();
    global.auth = isAuthenticated
    return (
        !isAuthenticated && (
            <button onClick={() => loginWithRedirect()}>
                Zaloguj się
            </button>
        )
    )
}

export default LoginButton
