import Page from '../../Components/Page';
import {
  Box,
  CircularProgress,
  Fade,
  IconButton,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
  Button,
} from '@mui/material';
import FormInfo from './FormInfo';
import DownloadForm from '../../Components/DownloadForm';
import { useEffect, useState } from 'react';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import SettingsIcon from '@mui/icons-material/Settings';
import { useParams } from 'react-router-dom';
import { apiCallGet } from '../../Utilities/ApiCalls';
import FormPermissionsModal from './FormPermissionsModal';

const Form = () => {
  const { id } = useParams();
  const [downloading, setDownloading] = useState(false);
  const [formData, setFormData] = useState<any>(null);
  const [isOwner, setIsOwner] = useState(false);
  const [showPermissions, setShowPermissions] = useState(false);
  const [permissions, setPermissions] = useState({
    allow_team_edit: true,
    allow_team_view: true,
    require_explicit_permissions: false,
  });

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    if (id) {
      const fetchFormData = async () => {
        const response = await apiCallGet(`api/sdg-action-plan/${id}/`, true);
        if (response?.statusCode === 200) {
          setFormData(response);
          setIsOwner(response.is_owner || false);
          if (response.permissions) {
            setPermissions(response.permissions);
          }
        } else {
          console.error(response);
        }
      };
      fetchFormData();
    }
  }, [id]);

  const handleFormDownload = async () => {
    setDownloading(true);
    if (id) {
      try {
        await DownloadForm(formData);
        console.log('download worked');
      } catch (error) {
        console.log(error);
      }
    }
    setDownloading(false);
  };

  return (
    <Page>
      <Box
        sx={{
          alignSelf: 'center',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
          width: isMobile ? '95%' : '80%',
          background: 'white',
          padding: isMobile ? '20px' : '30px',
          borderRadius: 2,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: isMobile ? 'column' : 'row',
            justifyContent: 'space-between',
            alignItems: isMobile ? 'flex-start' : 'center',
            gap: isMobile ? 2 : 0,
          }}
        >
          <Typography variant={isMobile ? 'h5' : 'h4'} paddingLeft={isMobile ? 0 : '30px'}>
            SDG Knowledge Action Plan
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            {isOwner && (
              <Button
                variant="outlined"
                color="primary"
                startIcon={<SettingsIcon />}
                onClick={() => setShowPermissions(true)}
                sx={{ textTransform: 'none' }}
              >
                MANAGE FORM PERMISSIONS
              </Button>
            )}
            <Tooltip title="Download Plan as PDF" arrow slots={{ transition: Fade }}>
              <IconButton onClick={handleFormDownload}>
                {downloading ? (
                  <CircularProgress size={20} />
                ) : (
                  <FileDownloadIcon sx={{ fontSize: 30 }} />
                )}
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        <FormInfo />
      </Box>
      {id && (
        <FormPermissionsModal
          open={showPermissions}
          onClose={() => setShowPermissions(false)}
          formId={id}
          initialPermissions={permissions}
        />
      )}
    </Page>
  );
};

export default Form;