
export const isAuthenticated = async () => {
    const reponse = await fetch('/api/check-auth')
    return reponse.ok
}

export const login = async (password) => {
    const data = {
        "password": password
    }
    const response = await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    if (response.ok) {
        return true
    }
    return false
}