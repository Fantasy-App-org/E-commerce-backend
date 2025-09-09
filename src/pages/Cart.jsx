import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Paper,
  Divider,
  Button,
  IconButton,
  TextField,
  Grid,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import api from '../api';
import { useNavigate } from 'react-router-dom';

const Cart = () => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchCart = async () => {
    try {
      const response = await api.get('/cart/');
      setCart(response.data);
    } catch (err) {
      console.error('Failed to fetch cart:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleUpdateQty = async (itemId, newQty) => {
    try {
      if (newQty <= 0) {
        await api.patch('/cart/update_item/', { item_id: itemId, qty: 0 });
      } else {
        await api.patch('/cart/update_item/', { item_id: itemId, qty: newQty });
      }
      fetchCart();
    } catch (err) {
      alert('Failed to update cart: ' + (err.response?.data?.detail || 'An error occurred.'));
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      try {
        await api.delete('/cart/clear/');
        fetchCart();
        alert('Cart cleared successfully.');
      } catch (err) {
        alert('Failed to clear cart.');
      }
    }
  };

  const handlePlaceOrder = async () => {
    try {
      await api.post('/orders/create/');
      alert('Order placed successfully!');
      navigate('/orders');
    } catch (err) {
      alert('Failed to place order: ' + (err.response?.data?.detail || 'An error occurred.'));
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <Typography variant="h5" align="center" mt={4}>
        Your cart is empty.
      </Typography>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>Shopping Cart</Typography>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <List>
          {cart.items.map((item) => (
            <ListItem
              key={item.id}
              divider
              sx={{ py: 2 }}
              secondaryAction={
                <IconButton edge="end" onClick={() => handleUpdateQty(item.id, 0)}>
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemAvatar>
                <Avatar
                  variant="square"
                  src={item.image || 'https://via.placeholder.com/50'}
                  alt={item.product_title}
                />
              </ListItemAvatar>
              <ListItemText
                primary={item.product_title}
                secondary={`₹${item.price_snapshot} x ${item.qty} = ₹${item.subtotal}`}
              />
              <Box sx={{ ml: 2, display: 'flex', alignItems: 'center' }}>
                <TextField
                  type="number"
                  value={item.qty}
                  onChange={(e) => handleUpdateQty(item.id, parseInt(e.target.value) || 0)}
                  size="small"
                  sx={{ width: 80 }}
                  inputProps={{ min: 0 }}
                />
              </Box>
            </ListItem>
          ))}
        </List>
        <Divider sx={{ my: 2 }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Total:</Typography>
          <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
            ₹{cart.total}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button variant="outlined" color="error" onClick={handleClearCart}>
            Clear Cart
          </Button>
          <Button variant="contained" onClick={handlePlaceOrder}>
            Place Order
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Cart;