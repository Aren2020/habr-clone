import { useLocation, Navigate, Outlet } from "react-router-dom";
import Cookies from 'js-cookie'

import React from 'react'

const RequireAuth = () => {
  const accessToken = Cookies.get('accessToken');
  const refreshToken = Cookies.get('refreshToken');

  return (
    (accessToken && refreshToken)
        ? <Outlet />
        : <Navigate to="/login" state={{ from: location }} replace />
  )
}

export default RequireAuth;