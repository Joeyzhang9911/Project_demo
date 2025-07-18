import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  SelectChangeEvent,
} from '@mui/material';
import {
  Timeline,
  Search,
  Edit,
  Visibility,
  TrendingUp,
  AccessTime,
} from '@mui/icons-material';
import { apiCallGet } from '../Utilities/ApiCalls';
import Page from '../Components/Page';

interface AnalyticsData {
  page_activities: {
    total_visits: number;
    total_active_time: number;
    most_visited_pages: Array<{
      page_name: string;
      visit_count: number;
    }>;
    average_session_time: number;
  };
  search_activities: {
    total_searches: number;
    search_types: Array<{
      search_type: string;
      search_count: number;
    }>;
    most_searched_terms: Array<{
      search_query: string;
      search_count: number;
    }>;
  };
  form_activities: {
    total_form_activities: number;
    form_edit_time: number;
    total_words_written: number;
    most_active_forms: Array<{
      form_id__impact_project_name: string;
      activity_count: number;
    }>;
  };
}

const UserActivityAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [timeRange, setTimeRange] = useState<string>('all');
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await apiCallGet(
        `api/admin/analytics/user-activity/?time_range=${timeRange}`,
        true
      );
      
      if (response?.statusCode === 200) {
        setAnalyticsData(response);
      }
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <Page>
        <Box p={3}>
          <LinearProgress />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading...
          </Typography>
        </Box>
      </Page>
    );
  }

  return (
    <Page>
      <Box p={3}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" gutterBottom>
            User Activity Analytics
          </Typography>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e: SelectChangeEvent) => setTimeRange(e.target.value)}
            >
              <MenuItem value="all">All Time</MenuItem>
              <MenuItem value="week">Last Week</MenuItem>
              <MenuItem value="month">Last Month</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* 概览卡片 */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Visibility color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Page Visits</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {analyticsData?.page_activities.total_visits || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Visits
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Search color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Searches</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {analyticsData?.search_activities.total_searches || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Searches
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Edit color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Form Activities</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {analyticsData?.form_activities.total_form_activities || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Form Activities
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <AccessTime color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Active Time</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {formatTime(analyticsData?.page_activities.total_active_time || 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Active Time
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* 详细分析标签页 */}
        <Card>
          <Tabs value={activeTab} onChange={(e: React.SyntheticEvent, newValue: number) => setActiveTab(newValue)}>
            <Tab label="Page Activities" />
            <Tab label="Search Behaviors" />
            <Tab label="Form Behaviors" />
          </Tabs>
          
          <Box p={3}>
            {activeTab === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Page Visit Statistics
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Most Visited Pages
                    </Typography>
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Page Name</TableCell>
                            <TableCell align="right">Visit Count</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analyticsData?.page_activities.most_visited_pages.map((page: any, index: number) => (
                            <TableRow key={index}>
                              <TableCell>{page.page_name}</TableCell>
                              <TableCell align="right">{page.visit_count}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Session Time Statistics
                    </Typography>
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        Average Session Time: {formatTime(analyticsData?.page_activities.average_session_time || 0)}
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        Total Active Time: {formatTime(analyticsData?.page_activities.total_active_time || 0)}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {activeTab === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Search Behavior Analysis
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Search Type Distribution
                    </Typography>
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Search Type</TableCell>
                            <TableCell align="right">Search Count</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analyticsData?.search_activities.search_types.map((type: any, index: number) => (
                            <TableRow key={index}>
                              <TableCell>{type.search_type}</TableCell>
                              <TableCell align="right">{type.search_count}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Most Searched Terms
                    </Typography>
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Search Query</TableCell>
                            <TableCell align="right">Search Count</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analyticsData?.search_activities.most_searched_terms.map((term: any, index: number) => (
                            <TableRow key={index}>
                              <TableCell>{term.search_query}</TableCell>
                              <TableCell align="right">{term.search_count}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {activeTab === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Form Behavior Analysis
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Most Active Forms
                    </Typography>
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Form Name</TableCell>
                            <TableCell align="right">Activity Count</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analyticsData?.form_activities.most_active_forms.map((form: any, index: number) => (
                            <TableRow key={index}>
                              <TableCell>{form.form_id__impact_project_name || 'Untitled Form'}</TableCell>
                              <TableCell align="right">{form.activity_count}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Edit Statistics
                    </Typography>
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        Total Edit Time: {formatTime(analyticsData?.form_activities.form_edit_time || 0)}
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        Total Words: {analyticsData?.form_activities.total_words_written || 0} words
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        Total Form Activities: {analyticsData?.form_activities.total_form_activities || 0} times
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            )}
          </Box>
        </Card>
      </Box>
    </Page>
  );
};

export default UserActivityAnalytics; 