import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  TextField,
  Autocomplete,
  Divider,
  Alert,
  CircularProgress,
  FormGroup,
  Checkbox,
} from '@mui/material';
import { Close as CloseIcon, Add as AddIcon, Remove as RemoveIcon } from '@mui/icons-material';
import { apiCallGet, apiCallPost } from '../../Utilities/ApiCalls';

interface FormPermissionsModalProps {
  open: boolean;
  onClose: () => void;
  formId: string;
  initialPermissions?: {
    allow_team_edit: boolean;
    allow_team_view: boolean;
    require_explicit_permissions: boolean;
  };
}

interface User {
  id: number;
  username: string;
  email: string;
}

interface TeamMember {
  id: number;
  username: string;
  email: string;
  role: string;
}

const FormPermissionsModal: React.FC<FormPermissionsModalProps> = ({
  open,
  onClose,
  formId,
  initialPermissions = {
    allow_team_edit: true,
    allow_team_view: true,
    require_explicit_permissions: false,
  },
}) => {
  const [permissions, setPermissions] = useState(initialPermissions);
  const [editors, setEditors] = useState<User[]>([]);
  const [viewers, setViewers] = useState<User[]>([]);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [originalEditors, setOriginalEditors] = useState<User[]>([]);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    setPermissions(initialPermissions);
  }, [initialPermissions]);

  useEffect(() => {
    if (open && formId) {
      loadPermissionsData();
    }
  }, [open, formId]);

  const loadPermissionsData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load form basic information (including permission settings)
      const formData = await apiCallGet(`api/sdg-action-plan/${formId}/`, true);
      if (formData.statusCode === 200) {
        setPermissions({
          allow_team_edit: formData.allow_team_edit ?? true,
          allow_team_view: formData.allow_team_view ?? true,
          require_explicit_permissions: formData.require_explicit_permissions ?? false,
        });
      }

      // Load editors list
      const editorsData = await apiCallGet(`api/sdg-action-plan/${formId}/editors/`, true);
      if (editorsData.statusCode === 200) {
        setEditors(editorsData.editors || []);
        setOriginalEditors(editorsData.editors || []);
      }

      // Load viewers list
      const viewersData = await apiCallGet(`api/sdg-action-plan/${formId}/viewers/`, true);
      if (viewersData.statusCode === 200) {
        setViewers(viewersData.viewers || []);
      }

      // Load team members list (for selecting editors and viewers)
      const teamData = await apiCallGet(`api/teams/${formData.team}/members/`, true);
      if (teamData.statusCode === 200) {
        // Convert team member data format
        const members = teamData.members || [];
        const formattedMembers = members.map((member: any) => ({
          id: member.user.id,
          username: member.user.username,
          email: member.user.email,
          role: member.role
        }));
        setTeamMembers(formattedMembers);
      }

    } catch (err) {
      setError('Failed to load permissions data');
      console.error('Error loading permissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (name: keyof typeof permissions) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setPermissions(prev => ({
      ...prev,
      [name]: event.target.checked,
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await apiCallPost(`api/sdg-action-plan/${formId}/permissions/`, permissions, true);
      if (response.statusCode === 200) {
        setMessage({ type: 'success', text: 'Permissions updated successfully' });
        setTimeout(() => {
          onClose();
          setMessage(null);
        }, 1500);
      } else {
        setMessage({ type: 'error', text: response.message || 'Failed to update permissions' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'An error occurred while updating permissions' });
    }
    setLoading(false);
  };

  // 过滤掉已经是编辑者的团队成员
  const availableEditors = teamMembers.filter(
    member => !editors.some(editor => editor.id === member.id)
  );

  // 过滤掉已经是查看者的团队成员
  const availableViewers = teamMembers.filter(
    member => !viewers.some(viewer => viewer.id === member.id)
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            Permission Settings
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : (
          <>
            <Typography variant="h6" gutterBottom>
              Team Permission Settings
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={permissions.allow_team_edit}
                  onChange={handleChange('allow_team_edit')}
                />
              }
              label="Allow team members to edit"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={permissions.allow_team_view}
                  onChange={handleChange('allow_team_view')}
                />
              }
              label="Allow team members to view"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={permissions.require_explicit_permissions}
                  onChange={handleChange('require_explicit_permissions')}
                />
              }
              label="Require explicit permissions for team members"
            />
            
            <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
              <Typography variant="body2">
                <strong>Note:</strong> Team owners and form creators always have full access. 
                When explicit permissions are enabled, only selected members can edit the form.
              </Typography>
            </Alert>
            
            {permissions.require_explicit_permissions && (
              <>
                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Select Editors
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Choose team members who can edit this form:
                </Typography>
                <FormGroup>
                  {teamMembers.map((member) => (
                    <FormControlLabel
                      key={member.id}
                      control={
                        <Checkbox
                          checked={editors.some(editor => editor.id === member.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setEditors(prev => [...prev, member]);
                            } else {
                              setEditors(prev => prev.filter(editor => editor.id !== member.id));
                            }
                          }}
                        />
                      }
                      label={`${member.username} (${member.role})`}
                    />
                  ))}
                </FormGroup>
                
                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Select Viewers
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Choose team members who can view this form:
                </Typography>
                <FormGroup>
                  {teamMembers.map((member) => (
                    <FormControlLabel
                      key={member.id}
                      control={
                        <Checkbox
                          checked={viewers.some(viewer => viewer.id === member.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setViewers(prev => [...prev, member]);
                            } else {
                              setViewers(prev => prev.filter(viewer => viewer.id !== member.id));
                            }
                          }}
                        />
                      }
                      label={`${member.username} (${member.role})`}
                    />
                  ))}
                </FormGroup>
              </>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          disabled={loading}
        >
          Save Changes
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FormPermissionsModal; 