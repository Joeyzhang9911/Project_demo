import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import InputField from './LoginInputField';
import { Alert, Typography } from '@mui/material';
import { apiCallPost } from '../Utilities/ApiCalls';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { useGoogleLogin } from './GoogleLogin';
import { Checkbox, FormControlLabel } from '@mui/material';

const SignUpForm = () => {

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [revealed, setRevealed] = useState<'password' | 'text'>('password');
  const [email, setEmail] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [errorMessage, setErrorMessage] = useState<string[]>([]);

  const navigate = useNavigate();

  const { handleGoogleLoginSuccess, handleGoogleLoginError } = useGoogleLogin();
  
  // API Call Here
  const signup = async () => {
    const data = await apiCallPost('api/auth/pending-register/', { username, email, password1: password, password2: confirmPassword, mobile: phoneNumber }, false);
    if (data.token) {
      navigate('/confirmation-pin', {
        state: {
          username,
          email,
          password1: password,
          password2: confirmPassword,
          mobile: phoneNumber,
          initialToken: data.token
        }}
      )
    } else {
      const errors: string[] = [];
      for (let field in data) {
        if (field !== 'statusCode') {
          if (field === 'non_field_errors') {
            errors.push(data[field][0]);
          } else {
            errors.push(field.toUpperCase() + ': ' + data[field][0]);
          }
        }
      }
      setErrorMessage(errors);
    }
  };

  // Show Password
  const handleToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRevealed(event.target.checked ? 'text' : 'password');
  };

  return (
    <Box sx={{
      boxSizing: 'border-box',
      width: { xs: '100%', sm: '50%' },
      maxWidth: '100%',
      padding: 3, 
      backgroundColor: 'white', 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center',
      borderRadius: { xs: '0 0 8px 8px', sm: '0 8px 8px 0' }
    }}>
      <Typography style={{ fontSize: '1.6rem', fontWeight: 'bold', marginBottom: '20px', textAlign: 'center' }}>SDG Knowledge Sign Up</Typography>

      {errorMessage.length > 0 && 
        (<Alert severity='error' sx={{ marginBottom: '15px' }}>
          {errorMessage.map((error, index) => (
            <Typography key={index} sx={{ fontSize: '0.85rem' }}>
              {error}
            </Typography>
          ))}
        </Alert>)
      }

      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-around',
        alignItems: 'center', 
        flexDirection: 'column',
        gap: '10px',
        width: '80%'
      }}>
        <InputField 
          type='text'
          name='username' 
          placeholder='Username'
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <InputField 
          type='text'
          name='contact' 
          placeholder='Email'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <InputField 
          type='text'
          name='phonenumber' 
          placeholder='Phone Number (optional)'
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
        />
        <InputField 
          type={revealed}
          name='password' 
          placeholder='Password'
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <InputField 
          type={revealed}
          name='confirmpassword' 
          placeholder='Confirm Password'
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
        <FormControlLabel
          sx={{ m: 0, '& .MuiFormControlLabel-label': { fontSize: '0.75rem' } }}
          control={
            <Checkbox
              size='small'
              checked={revealed === 'text'}
              onChange={handleToggle}
            />
          }
          label='Show Password'
        />

        <Button
          variant='contained'
          size='small' 
          sx={{
            backgroundColor: '#000000',
            width: '85%',
            fontSize: '10px',
            textTransform: 'none',
            boxShadow: 'none'
          }}
          onClick={signup}
        >
          Sign Up
        </Button>
        
        <Divider 
          sx={{ 
            width: '100%', 
            color: '#828282',
            fontSize: '10px', 
            mt: '7px'
          }}
        >
          or continue with
        </Divider>

        <GoogleLogin
          onSuccess={handleGoogleLoginSuccess}
          onError={handleGoogleLoginError}
          useOneTap={false}
          theme='outline'
          size='medium'
          text='continue_with'
          width='100%'
        />
        
        <div style={{
          color: '#828282',
          fontSize: '10px',
          marginTop: '5px',
          textAlign: 'center'
        }}>
          By clicking continue, you agree to our&nbsp;
          <a href="https://policies.google.com/terms?hl=en" style={{ color: '#000000' }}>Terms of Service</a>
            &nbsp;
            and&nbsp;
            <a href="https://policies.google.com/privacy?hl=en" style={{ color: '#000000' }}>Privacy Policy</a>
        </div>

      </Box>
    </Box>
  );
};

export default SignUpForm;
