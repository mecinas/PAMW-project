import React from 'react'
import { useAuth0 } from '@auth0/auth0-react';


const LogoutButton = () => {
    const { logout, isAuthenticated } = useAuth0();
    global.auth = isAuthenticated
    return (
        isAuthenticated && (
            <button onClick={() => logout()}>
                Wyloguj się
            </button>
        )
    )
}

export default LogoutButton
