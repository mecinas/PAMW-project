import React from 'react'
import { useAuth0 } from '@auth0/auth0-react';

const Account = () => {
    const { user, isAuthenticated } = useAuth0();
    global.account = JSON.stringify(user, null, 2)
    return (
        isAuthenticated && (
            <div>
                Konto użytkownika: {user.name}
            </div>
        )
    )
}

export default Account
