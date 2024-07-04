import { apiSlice } from "../../app/api/apiSlice";
import '../../scss/auth.css';

export const authApiSlice = apiSlice.injectEndpoints({
    endpoints: builder => ({
        login: builder.mutation({
            query: credentials => ({
                url: 'users/login/',
                method: 'POST',
                body: { ...credentials },
            })
        }),
        signup: builder.mutation({
            query: credentials => ({
                url: 'users/registration/',
                method: 'POST',
                body: { ...credentials },
            })
        }),
    })
})

export const {
    useLoginMutation,
    useSignupMutation,
} = authApiSlice;