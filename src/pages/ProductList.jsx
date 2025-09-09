// src/pages/ProductList.jsx
import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Box,
  CircularProgress,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import api from '../api';
import ProductCard from '../components/ProductCard';

const ProductList = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    category__slug: '',
    ordering: '-created_at',
  });

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/products/', { params: filters });
      // The backend returns a paginated response with a 'results' key
      setProducts(response.data.results);
    } catch (err) {
      setError('Failed to fetch products. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories/');
      // The backend returns a plain list of categories
      if (Array.isArray(response.data)) {
        setCategories(response.data);
      }
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleFilterChange = (event) => {
    setFilters({ ...filters, [event.target.name]: event.target.value });
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>Products</Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            size="small"
            label="Search Products"
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Category</InputLabel>
            <Select
              name="category__slug"
              value={filters.category__slug}
              label="Category"
              onChange={handleFilterChange}
            >
              <MenuItem value="">All</MenuItem>
              {categories.map((cat) => (
                <MenuItem key={cat.id} value={cat.slug}>
                  {cat.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={6} sm={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Sort By</InputLabel>
            <Select
              name="ordering"
              value={filters.ordering}
              label="Sort By"
              onChange={handleFilterChange}
            >
              <MenuItem value="-created_at">Newest</MenuItem>
              <MenuItem value="price">Price: Low to High</MenuItem>
              <MenuItem value="-price">Price: High to Low</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <Grid container spacing={4}>
          {products.map((product) => (
            <Grid item key={product.id} xs={12} sm={6} md={4} lg={3}>
              <ProductCard product={product} />
            </Grid>
          ))}
        </Grid>
      )}
      {products.length === 0 && !loading && !error && (
        <Typography variant="h6" align="center" mt={4}>
          No products found.
        </Typography>
      )}
    </Container>
  );
};

export default ProductList;