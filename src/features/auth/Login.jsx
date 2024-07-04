import '../../scss/auth.css';
import { useRef, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLoginMutation } from "./authApiSlice";
import Cookies from 'js-cookie';

const Login = () => {
  const navigate = useNavigate();

  const userRef = useRef(null);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errMsg, setErrMsg] = useState('');

  const [login, { isLoading }] = useLoginMutation();

  useEffect(() => {
    userRef.current.focus();
  }, []);

  useEffect(() => {
    setErrMsg('');
  }, [username, password]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const userData = await login({ username, password }).unwrap();
      console.log(userData);
      //set cookies
      Cookies.set('accessToken', userData.accessToken, { secure: true, expires: 1 });
      Cookies.set('refreshToken', userData.refreshToken, { secure: true, expires: 1 });

      // navigate('/');
    } catch(err) {
      if (!err?.originalStatus) {
          setErrMsg('No Server Response!');
      } else if (err.originalStatus === 400) {
          setErrMsg('Missing Username or Password!');
      } else if (err.originalStatus === 401) {
          setErrMsg('Unauthorized!');
      } else {
          setErrMsg('Login Failed!');
      }
    }
  }

  const handleUserInput = e => setUsername(e.target.value);
  const handlePwdInput = e => setPassword(e.target.value);

  const content = isLoading ? <h1>Loading...</h1> : (
    <div>
        <h1>Login to your account</h1>
        <form onSubmit={handleSubmit}>
            <div className="mb-3">
                <label htmlFor="inputUserName" className="form-label">Email or Username</label>
                <input onChange={handleUserInput} ref={userRef} type="text" name="username" className="form-control" id="inputUserName" aria-describedby="emailHelp" />
                <div id="emailHelp" className="form-text">We'll never share your email with anyone else.</div>
            </div>
            <div className="mb-3">
                <label htmlFor="exampleInputPassword1" className="form-label">Password</label>
                <input onChange={handlePwdInput} type="password" name="password" className="form-control" id="exampleInputPassword1" />
            </div>
            {errMsg && (<p className={errMsg} aria-live="assertive">{errMsg}</p>)}
            <button type="submit" className="btn btn-primary">Submit</button>
        </form>
    </div>
  )

  return content;
}

export default Login;