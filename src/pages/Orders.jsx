import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import api from '../api';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders/');
      setOrders(response.data);
    } catch (err) {
      console.error('Failed to fetch orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (orders.length === 0) {
    return (
      <Typography variant="h5" align="center" mt={4}>
        You have not placed any orders yet.
      </Typography>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>My Orders</Typography>
      {orders.map((order) => (
        <Paper key={order.id} elevation={3} sx={{ mb: 2, borderRadius: 2 }}>
          <Accordion>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{ bgcolor: 'grey.100' }}
            >
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h6">Order #{order.id}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Status: {order.status} | Total: ₹{order.total} | Date: {new Date(order.created_at).toLocaleDateString()}
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="subtitle1" gutterBottom>Items:</Typography>
              <List dense>
                {order.items.map((item) => (
                  <ListItem key={item.id}>
                    <ListItemText
                      primary={`${item.title_snapshot} x ${item.qty}`}
                      secondary={`Price: ₹${item.price_snapshot} | Subtotal: ₹${item.subtotal}`}
                    />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        </Paper>
      ))}
    </Container>
  );
};

export default Orders;