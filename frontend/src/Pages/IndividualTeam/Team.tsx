import Page from '../../Components/Page';
import TeamHeader from './TeamHeader';
import TeamMembersTable from './TeamMembersTable';
import { roleFromString, TeamRoles } from './TeamRole';
import React from 'react';
import { apiCallGet, apiCallPost } from '../../Utilities/ApiCalls';
import { useNavigate } from 'react-router-dom';

const Team = ({ teamId }: {teamId: string}) => {
  const [permission, setPermission] = React.useState(TeamRoles.Member);
  const [name, setName] = React.useState('');
  const navigate = useNavigate();

  // Initial retrieval of individual team
  React.useEffect(() => {
    const baseUrl = 'api/teams/' + teamId;
    const getUserPermissions = async () => {
      const data = await apiCallPost(baseUrl + '/role/', undefined, true);
      if (data.statusCode === 200) {
        // Sets permission for how the user can interact with the page
        // e.g., owner can promote or demote other users
        setPermission(roleFromString(data.role, data.can_invite, false));
      } else {
        navigate('/teams');
      }
    }
    const getGroupName = async () => {
      const data = await apiCallGet(baseUrl, true);
      if (data.statusCode === 200) {
        setName(data.name)
      } else {
        navigate('/teams');
      }
    }
    getUserPermissions();
    getGroupName();
  }, [teamId, navigate]); 

  return (
    <Page>
    {name.length > 0 &&
      (<React.Fragment>
        <TeamHeader groupName={name} />
        <TeamMembersTable permission={permission} teamId={teamId} groupName={name}
          setPermission={setPermission}/>
      </React.Fragment>)
    }
    </Page>
  )
}

export default Team;