import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "../api"; // your axios instance
import {
  CircularProgress,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardMedia,
  Rating,
  TextField,
  Divider,
  List,
  ListItem,
  ListItemText,
  Alert,
} from "@mui/material";
import { toast } from "react-toastify";

const ProductDetail = () => {
  const { slug } = useParams();
  const [product, setProduct] = useState(null);
  const [mainImage, setMainImage] = useState(null);
  const [loading, setLoading] = useState(true);

  // Reviews
  const [reviews, setReviews] = useState([]);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [reviewError, setReviewError] = useState("");

  useEffect(() => {
    fetchProduct();
    fetchReviews();
  }, [slug]);

  const fetchProduct = () => {
    setLoading(true);
    axios
      .get(`/products/${slug}/`)
      .then((res) => {
        setProduct(res.data);
        if (res.data.images && res.data.images.length > 0) {
          setMainImage(res.data.images[0].image);
        }
      })
      .catch((err) => console.error("Error fetching product:", err))
      .finally(() => setLoading(false));
  };

  const fetchReviews = () => {
    setReviewLoading(true);
    axios
      .get(`/products/${slug}/reviews/`)
      .then((res) => setReviews(res.data))
      .catch((err) => console.error("Error fetching reviews:", err))
      .finally(() => setReviewLoading(false));
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (rating < 1) {
      setReviewError("Please select a rating.");
      return;
    }
    try {
      await axios.post(`/products/${slug}/reviews/`, { rating, comment });
      setRating(0);
      setComment("");
      setReviewError("");
      fetchReviews();
    } catch (err) {
      console.error("Error posting review:", err);
      setReviewError("Failed to submit review. Are you logged in?");
    }
  };

  const handleAddToCart = async () => {
    try {
      await axios.post("/cart/add/", {
        product_id: product.id,
        qty: 1, // Default quantity
      });
      toast.success("Added to cart!");
    } catch (err) {
      console.error("Error adding to cart:", err);
      if (err.response && err.response.status === 401) {
        toast.error("Please log in to add items to your cart.");
      } else {
        toast.error("Failed to add to cart.");
      }
    }
  };

  if (loading) {
    return (
      <Box sx={{ textAlign: "center", mt: 5 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!product) {
    return (
      <Typography variant="h6" sx={{ textAlign: "center", mt: 5 }}>
        Product not found
      </Typography>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto", p: 3 }}>
      <Grid container spacing={4}>
        {/* Product Images */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              width: "100%",
              height: { xs: 250, md: 400 },
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: "#f9f9f9",
              borderRadius: 2,
            }}
          >
            {mainImage ? (
              <CardMedia
                component="img"
                image={mainImage}
                alt={product.title}
                sx={{
                  maxWidth: "100%",
                  maxHeight: "100%",
                  objectFit: "contain",
                  borderRadius: 2,
                }}
              />
            ) : (
              <Typography>No Image Available</Typography>
            )}
          </Card>

          {product.images && product.images.length > 1 && (
            <Box sx={{ display: "flex", gap: 1, mt: 2, overflowX: "auto", pb: 1 }}>
              {product.images.map((img, idx) => (
                <Card
                  key={idx}
                  onClick={() => setMainImage(img.image)}
                  sx={{
                    width: 70,
                    height: 70,
                    cursor: "pointer",
                    border: img.image === mainImage ? "2px solid #1976d2" : "1px solid #ddd",
                  }}
                >
                  <CardMedia
                    component="img"
                    image={img.image}
                    alt={`Thumbnail ${idx}`}
                    sx={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                </Card>
              ))}
            </Box>
          )}
        </Grid>

        {/* Product Info */}
        <Grid item xs={12} md={6}>
          <Typography variant="h4" gutterBottom>
            {product.title}
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, color: "text.secondary" }}>
            {product.description}
          </Typography>
          <Typography variant="h5" color="primary" sx={{ fontWeight: "bold" }}>
            ₹{product.price}
          </Typography>
          {product.mrp && (
            <Typography
              variant="body2"
              sx={{ textDecoration: "line-through", color: "gray", mb: 2 }}
            >
              MRP: ₹{product.mrp}
            </Typography>
          )}
          <Typography sx={{ mb: 1 }}>Brand: {product.brand || "N/A"}</Typography>
          <Typography sx={{ mb: 3 }}>In Stock: {product.stock}</Typography>

          <Button
            variant="contained"
            color="primary"
            size="large"
            sx={{ mt: 2 }}
            onClick={handleAddToCart}
          >
            Add to Cart
          </Button>
        </Grid>
      </Grid>

      {/* Reviews Section */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="h5" gutterBottom>
          Customer Reviews
        </Typography>
        <Divider sx={{ mb: 3 }} />

        {/* Existing Reviews */}
        {reviewLoading ? (
          <CircularProgress />
        ) : reviews.length === 0 ? (
          <Typography>No reviews yet. Be the first to review!</Typography>
        ) : (
          <List>
            {reviews.map((rev) => (
              <ListItem key={rev.id} alignItems="flex-start" sx={{ borderBottom: "1px solid #eee" }}>
                <ListItemText
                  primary={
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Rating value={rev.rating} readOnly size="small" />
                      <Typography variant="body2" color="text.secondary">
                        by {rev.user_name}
                      </Typography>
                    </Box>
                  }
                  secondary={rev.comment}
                />
              </ListItem>
            ))}
          </List>
        )}

        {/* Add Review Form */}
        <Box component="form" onSubmit={handleReviewSubmit} sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Write a Review
          </Typography>
          {reviewError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {reviewError}
            </Alert>
          )}
          <Rating
            value={rating}
            onChange={(e, newValue) => setRating(newValue)}
            size="large"
            sx={{ mb: 2 }}
          />
          <TextField
            label="Your Comment"
            multiline
            rows={3}
            fullWidth
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button type="submit" variant="contained" color="primary">
            Submit Review
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default ProductDetail;
