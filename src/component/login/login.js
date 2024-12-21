import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
} from "firebase/auth";
import auth from "../../firebaseconfig";

const Login = () => {
  const [loginError, setLoginError] = useState("");
  const [success, setSuccess] = useState("");
  const emailRef = useRef(null);
  const navigate = useNavigate(); // useNavigate should be inside the component

  const handleLogin = (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    const password = e.target.password.value;

    setLoginError("");
    setSuccess("");

    // Attempt to sign in with email and password
    signInWithEmailAndPassword(auth, email, password)
      .then((result) => {
        // Check if the user's email is verified
        if (result.user) {
          setSuccess("Logged in Successfully");
          navigate("/main"); // Redirect to the main page after successful login
        } else {
          alert("Please verify your email");
        }
      })
      .catch((error) => {
        setLoginError(error.message); // Display the error if login fails
      });
  };

  const handleForgetPassword = () => {
    const email = emailRef.current.value; // Correcting this part to access the email value properly
    if (!email) {
      console.log("Please provide an email");
      return;
    } else if (
      !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)
    ) {
      console.log("Please write a valid email");
      return;
    }

    // Send a password reset email
    sendPasswordResetEmail(auth, email)
      .then(() => {
        alert("Please check your email for password reset instructions");
      })
      .catch((error) => {
        console.log(error); // Handle error on sending password reset email
      });
  };

  return (
    <div>
      {/* Login form */}
      <div className="hero min-h-screen bg-base-200">
        <div className="hero-content flex-col lg:flex-row-reverse">
          <div className="card flex-shrink-0 w-full max-w-sm shadow-2xl bg-base-100">
            <div className="card-body">
              <form onSubmit={handleLogin}>
                {/* Email input */}
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Email</span>
                  </label>
                  <input
                    type="text"
                    name="email"
                    placeholder="Email"
                    ref={emailRef}
                    className="input input-bordered"
                  />
                </div>

                {/* Password input */}
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Password</span>
                  </label>
                  <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    className="input input-bordered"
                  />
                  <label className="label">
                    <a
                      onClick={handleForgetPassword}
                      href="#"
                      className="label-text-alt link link-hover"
                    >
                      Forgot password?
                    </a>
                  </label>
                </div>

                {/* Submit button */}
                <div className="form-control mt-6">
                  <button className="btn btn-primary">Login</button>
                </div>
              </form>

              {/* Display login error and success messages */}
              {loginError && <p className="text-red-700">{loginError}</p>}
              {success && <p className="text-green-600">{success}</p>}

              {/* Link to Sign-Up */}
              <p>
                New to this website? Please <Link to="/sign-up">Register</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
