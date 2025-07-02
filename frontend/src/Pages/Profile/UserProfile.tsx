import Page from '../../Components/Page';
import { useState, useEffect } from 'react';
import { useMediaQuery, useTheme } from '@mui/material';
import { Box } from '@mui/material';
import InputField from '../../Components/UserProfileInputField';
import PageButton, { PageButtonColour } from '../../Components/PageButton';
import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';
import ProfileCard from '../../Components/ProfileCard';
import { apiCallGet, apiCallPut } from '../../Utilities/ApiCalls';
import { useParams } from 'react-router-dom';
import UserDeleteModal from './UserDeleteModal';

const UserProfile = () => {
  const { targetUsername } = useParams();
  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [number, setNumber] = useState('');
  const [organisation, setOrganisation] = useState('');
  const [facultyMajor, setFacultyMajor] = useState('');

  const [initialFirstName, setInitialFirstName] = useState('');
  const [initialLastName, setInitialLastName] = useState('');
  const [initialEmail, setInitialEmail] = useState('');
  const [initialNumber, setInitialNumber] = useState('');
  const [initialOrganisation, setInitialOrganisation] = useState('');
  const [initialFacultyMajor, setInitialFacultyMajor] = useState('');
  
  const [editing, setEditing] = useState(false);
  
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));

  const [key, setKey] = useState(0);

  useEffect(() => {
    const getData = async () => {
      if (targetUsername) {
        return await apiCallGet('api/auth/profile/' + targetUsername + '/', true);
      }
      return await apiCallGet('api/auth/profile/', true);
    }

    const fetchData = async () => {
      const data = await getData();
      setUsername(data.username);
      setFirstName(data.first_name);
      setLastName(data.last_name);
      setEmail(data.email);
      setNumber(data.mobile);
      setOrganisation(data.organization);
      setFacultyMajor(data.faculty_and_major);
      setInitialFirstName(data.first_name);
      setInitialLastName(data.last_name);
      setInitialEmail(data.email);
      setInitialNumber(data.mobile);
      setInitialOrganisation(data.organization);
      setInitialFacultyMajor(data.faculty_and_major);
    }
    fetchData();
  }, [targetUsername])
  
  const updateUserDetails = async () => {
    const updatedData = {
      username: username,
      first_name: firstName,
      last_name: lastName,
      email: email,
      mobile: number,
      organization: organisation,
      faculty_and_major: facultyMajor
    };
    
    const data = await apiCallPut('api/auth/profile/', updatedData, true);

    setInitialFirstName(data.first_name);
    setInitialLastName(data.last_name);
    setInitialEmail(data.email);
    setInitialNumber(data.mobile);
    setInitialOrganisation(data.organization);
    setInitialFacultyMajor(data.faculty_and_major);

    // If all details can be saved
    toggleEditing();

  }

  const toggleEditing = () => {
    setEditing(!editing);
  }

  const handleCancel = () => {
    // Change back to inital inputs
    setFirstName(initialFirstName);
    setLastName(initialLastName);
    setEmail(initialEmail);
    setNumber(initialNumber);
    setOrganisation(initialOrganisation);
    setFacultyMajor(initialFacultyMajor);

    setKey(prev => prev + 1);

    toggleEditing();
  };

  return (
    <Page center>
      <Box sx={{ 
        mx: 'auto',
        width: '100%', 
        height: '100%', 
        padding: 3, 
        display: 'flex', 
        justifyContent: 'space-evenly',
        alignItems: 'stretch',
        flexDirection: isSmallScreen ? 'column' : 'row'
        
      }}>
        <ProfileCard username={username}/>
        
        <Box 
          key={key} 
          sx={{
            flexGrow: 1,
            height: '100%',
            display: 'flex'
          }}
        >
          <Box sx={{
            width: '50%',
            height: '100%',
            minWidth: '30px',
            minHeight: '30px',
            padding: '30px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'flex-start'
          }}>
            <InputField 
              name='Username' 
              value={username} 
              onChange={(e) => setUsername(e.target.value)}
              editing={false}
              noDefault
            />
            <InputField 
              name='First Name' 
              value={firstName} 
              onChange={(e) => setFirstName(e.target.value)}
              editing={editing}
              key={key}
              noDefault
            />
            <InputField 
              name='Last Name' 
              value={lastName} 
              onChange={(e) => setLastName(e.target.value)}
              editing={editing}
              noDefault
            />
            <InputField 
              name='Email' 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              editing={editing}
              noDefault
            />
          </Box>
          
          <Box sx={{
            width: '50%',
            height: '100%',
            minWidth: '30px',
            minHeight: '30px',
            padding: '30px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <InputField 
              name='Phone Number' 
              value={number} 
              onChange={(e) => setNumber(e.target.value)}
              editing={editing}
              noDefault
            />
            <InputField 
              name='Organisation' 
              value={organisation} 
              onChange={(e) => setOrganisation(e.target.value)}
              editing={editing}
              noDefault
            />
            <InputField 
              name='Faculty and Major' 
              value={facultyMajor} 
              onChange={(e) => setFacultyMajor(e.target.value)}
              editing={editing}
              noDefault
            />
            <Box 
              sx={{ 
                marginTop: '30px',
                display: 'flex',
                justifyContent: 'flex-end'
              }}
            >
              { !targetUsername && (editing ? (
                <Box sx={{ display: 'flex', gap: '10px' }}>
                  <PageButton colour={PageButtonColour.Red} onClick={handleCancel}>Cancel</PageButton>
                  <PageButton colour={PageButtonColour.Green} startIcon={<SaveIcon />} onClick={updateUserDetails}>Save</PageButton>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', gap: '10px' }}>
                  <UserDeleteModal name={username} />
                  <PageButton colour={PageButtonColour.Blue} startIcon={<EditIcon />} onClick={toggleEditing}>Edit</PageButton>
                </Box>
              ))}
            </Box>
          </Box>
        </Box>
      </Box>
    </Page>
  );
};

export default UserProfile;