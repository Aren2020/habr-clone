import { useEffect, useRef, useState } from "react";
import { useSignupMutation } from "./authApiSlice"
import { useNavigate } from "react-router-dom";
import Cookies from 'js-cookie';

const Signup = () => {
  //signup component
  const userRef = useRef(null);
  const navigate = useNavigate();

  const [name, setName] = useState();
  const [lastName, setLastName] = useState(); 
  const [username, setUsername] = useState();
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [errMsg, setErrMsg] = useState('');
  
  const [signup, { isLoading }] = useSignupMutation();

  useEffect(() => {
    userRef.current.focus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
        const userData = await signup({ 
            name, lastName, username, email, password
        }).unwrap();
        console.log(userData);

        //set cookies
        Cookies.set('accessToken', userData.accessToken);
        Cookies.set('refreshToken', userData.refreshToken);

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

  const handleNameInput = e => setName(e.target.value);
  const handleLastNameInput = e => setLastName(e.target.value);
  const handleUserInput = e => setUsername(e.target.value);
  const handlePwdInput = e => setPassword(e.target.value);
  const handleEmailInput = e => setEmail(e.target.value);

  const content = isLoading ? <h1>Loading...</h1> : (
    <div>
        <h1>Create an account</h1>
        <form onSubmit={handleSubmit}>
            <div className="mb-3">
                <label htmlFor="inputName" className="form-label">Name</label>
                <input onChange={handleNameInput} ref={userRef} type="text" name="name" className="form-control" id="inputName" aria-describedby="emailHelp" />
            </div>
            <div className="mb-3">
                <label htmlFor="inputLastName" className="form-label">LastName</label>
                <input onChange={handleLastNameInput} ref={userRef} type="text" name="lastName" className="form-control" id="inputLastName" />
            </div>
            <div className="mb-3">
                <label htmlFor="inputUserName" className="form-label">Username</label>
                <input onChange={handleUserInput} type="text" name="username" className="form-control" id="inputUserName" />
            </div>
            <div className="mb-3">
                <label htmlFor="inputEmail" className="form-label">Email</label>
                <input onChange={handleEmailInput} type="email" name="email" className="form-control" id="inputEmail" aria-describedby="emailHelp" />
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

export default Signup