import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, CssBaseline } from '@mui/material';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import Signup from './pages/Signup';
import Login from './pages/Login';
import Profile from './pages/Profile';
import SellerRegistration from './pages/SellerRegistration';
import Notifications from './pages/Notifications';
import About from './pages/About';
import Home from './pages/Home';
import ProductList from './pages/ProductList';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Orders from './pages/Orders';
import SellerDashboard from './pages/seller/SellerDashboard';  // ✅ Corrected path
import SellerProducts from './pages/seller/SellerProducts';    // ✅ Corrected path
import SellerOrders from './pages/seller/SellerOrders';        // ✅ Corrected path
import VoucherPurchase from './pages/VoucherPurchase';
import MyVouchers from './pages/MyVouchers';
// ✅ Toastify imports
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <Router>
      <CssBaseline />
      <Navbar />
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Routes>
          {/* Public Pages */}
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />
          <Route path="/shop" element={<ProductList />} />
          <Route path="/product/:slug" element={<ProductDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/vouchers/purchase" element={<PrivateRoute><VoucherPurchase /></PrivateRoute>} />
          <Route path="/vouchers" element={<MyVouchers />} />



          {/* Authentication */}
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />

          {/* Protected Routes */}
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <Profile />
              </PrivateRoute>
            }
          />
          <Route
            path="/seller/register"
            element={
              <PrivateRoute>
                <SellerRegistration />
              </PrivateRoute>
            }
          />
          <Route
            path="/cart"
            element={
              <PrivateRoute>
                <Cart />
              </PrivateRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <PrivateRoute>
                <Orders />
              </PrivateRoute>
            }
          />
          <Route
            path="/notifications"
            element={
              <PrivateRoute>
                <Notifications />
              </PrivateRoute>
            }
          />

          {/* ✅ Seller Dashboard with Nested Pages */}
          <Route
            path="/seller/dashboard"
            element={
              <PrivateRoute>
                <SellerDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/seller/products"
            element={
              <PrivateRoute>
                <SellerProducts />
              </PrivateRoute>
            }
          />
          <Route
            path="/seller/orders"
            element={
              <PrivateRoute>
                <SellerOrders />
              </PrivateRoute>
            }
          />
        </Routes>
      </Container>

      {/* ✅ Toast Container for notifications */}
      <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} />
    </Router>
  );
}

export default App;
