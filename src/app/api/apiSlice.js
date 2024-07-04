import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import Cookies from 'js-cookie';

const baseQuery = fetchBaseQuery({
    baseUrl: 'http://locahost:8000/',
    credentials: "include",
    prepareHeaders: (headers, { getState }) => {
        const token = Cookies.get('accessToken');
        if(token) {
            headers.set('authorization', `Token ${token}`);
        }
        return headers;
    }
})

const baseQueryWithReauth = async (args, api, extraOptions) => {
    let result = await baseQuery(args, api, extraOptions);
    
    if(result?.error?.originalStatus === 401) {
        console.log('implementing refresh token...');
        
        const refreshResult = await baseQuery('users/updateTokens', api, extraOptions);
        console.log('update: ', refreshResult);

        if(refreshResult?.originalStatus === 200) {
            Cookies.set('accessToken', refreshResult.accessToken, { secure: true, expires: 1 });
            Cookies.set('refreshToken', refreshResult.refreshToken, { secure: true, expires: 1 });

            result = await baseQuery(args, api, extraOptions);
        } else {
            const refreshResult = await baseQuery('users/logout', api, extraOptions);
            console.log('logout: ', refreshResult);

            Cookies.remove('accessToken');
            Cookies.remove('refreshToken');
        }
    }

    return result;
}

export const apiSlice = createApi({
    baseQuery: baseQueryWithReauth,
    endpoints: builder => ({}),
})