#!/usr/bin/env python3
"""
Backend API Testing for MyApp Car Data Endpoints
Tests authentication and car data API endpoints as specified in the review request.
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://cargroup.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_user_registration(self):
        """Test user registration for authentication setup"""
        print("\n=== Testing Authentication Setup ===")
        
        url = f"{BACKEND_URL}/auth/register"
        payload = {
            "name": "Test Admin",
            "email": "admin@test.com",
            "password": "testpass123"
        }
        
        try:
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.log_test(
                        "User Registration", 
                        True, 
                        f"Successfully registered user and received JWT token",
                        {"user_id": data["user"]["id"], "user_name": data["user"]["name"]}
                    )
                    return True
                else:
                    self.log_test("User Registration", False, "Missing token or user in response", {"response": data})
                    return False
            elif response.status_code == 400:
                # User might already exist, try login instead
                return self.test_user_login()
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, f"Request failed: {str(e)}")
            return False
    
    def test_user_login(self):
        """Fallback login if registration fails due to existing user"""
        print("Attempting login with existing credentials...")
        
        url = f"{BACKEND_URL}/auth/login"
        payload = {
            "email": "admin@test.com",
            "password": "testpass123"
        }
        
        try:
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.auth_token = data["token"]
                    self.log_test(
                        "User Login (Fallback)", 
                        True, 
                        "Successfully logged in and received JWT token",
                        {"user_name": data["user"]["name"]}
                    )
                    return True
                else:
                    self.log_test("User Login (Fallback)", False, "Missing token in response", {"response": data})
                    return False
            else:
                self.log_test("User Login (Fallback)", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("User Login (Fallback)", False, f"Request failed: {str(e)}")
            return False
    
    def test_get_all_brands(self):
        """Test GET /api/car-data - Get all available car brands"""
        print("\n=== Testing Get All Car Brands ===")
        
        url = f"{BACKEND_URL}/car-data"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "brands" in data:
                    brands = data["brands"]
                    expected_brands = ["Tata", "Mahindra", "Kia", "Hyundai", "Honda", "Maruti", "Volkswagen", "Toyota"]
                    
                    if len(brands) == 8 and all(brand in brands for brand in expected_brands):
                        self.log_test(
                            "Get All Brands", 
                            True, 
                            f"Successfully retrieved all 8 brands",
                            {"brands": brands}
                        )
                        return True
                    else:
                        missing_brands = [b for b in expected_brands if b not in brands]
                        extra_brands = [b for b in brands if b not in expected_brands]
                        self.log_test(
                            "Get All Brands", 
                            False, 
                            f"Brand list mismatch. Expected 8 brands, got {len(brands)}",
                            {
                                "expected": expected_brands,
                                "actual": brands,
                                "missing": missing_brands,
                                "extra": extra_brands
                            }
                        )
                        return False
                else:
                    self.log_test("Get All Brands", False, "Missing 'brands' key in response", {"response": data})
                    return False
            else:
                self.log_test("Get All Brands", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("Get All Brands", False, f"Request failed: {str(e)}")
            return False
    
    def test_brand_data(self, brand: str, expected_models: List[str] = None):
        """Test GET /api/car-data/{brand} - Get specific brand car models"""
        url = f"{BACKEND_URL}/car-data/{brand}"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and data:
                    # Check if we have models
                    models = list(data.keys())
                    
                    if expected_models:
                        # Check if expected models are present
                        missing_models = [m for m in expected_models if m not in models]
                        if missing_models:
                            self.log_test(
                                f"Get {brand} Data", 
                                False, 
                                f"Missing expected models: {missing_models}",
                                {"expected": expected_models, "actual": models}
                            )
                            return False
                    
                    # Validate data structure: brand -> model -> variant -> transmission: price
                    valid_structure = True
                    structure_errors = []
                    
                    for model, variants in data.items():
                        if not isinstance(variants, dict):
                            structure_errors.append(f"Model '{model}' should have variants dict")
                            valid_structure = False
                            continue
                            
                        for variant, transmissions in variants.items():
                            if not isinstance(transmissions, dict):
                                structure_errors.append(f"Variant '{variant}' should have transmissions dict")
                                valid_structure = False
                                continue
                                
                            for transmission, price in transmissions.items():
                                if not isinstance(price, (int, float)) or price <= 0:
                                    structure_errors.append(f"Price for {model}-{variant}-{transmission} should be positive number")
                                    valid_structure = False
                    
                    if valid_structure:
                        self.log_test(
                            f"Get {brand} Data", 
                            True, 
                            f"Successfully retrieved {len(models)} models with valid structure",
                            {"models": models, "total_variants": sum(len(v) for v in data.values())}
                        )
                        return True
                    else:
                        self.log_test(
                            f"Get {brand} Data", 
                            False, 
                            f"Invalid data structure",
                            {"structure_errors": structure_errors}
                        )
                        return False
                        
                elif isinstance(data, dict) and not data:
                    # Empty dict is valid for non-existent brands
                    self.log_test(
                        f"Get {brand} Data", 
                        True, 
                        "Correctly returned empty object for invalid brand",
                        {"response": data}
                    )
                    return True
                else:
                    self.log_test(
                        f"Get {brand} Data", 
                        False, 
                        "Response should be a dictionary",
                        {"response_type": type(data), "response": data}
                    )
                    return False
            else:
                self.log_test(f"Get {brand} Data", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test(f"Get {brand} Data", False, f"Request failed: {str(e)}")
            return False
    
    def test_tata_models(self):
        """Test Tata brand with expected models"""
        print("\n=== Testing Tata Car Models ===")
        expected_models = ["Tiago", "Tigor", "Altroz", "Punch", "Nexon", "Curvv", "Harrier", "Safari"]
        return self.test_brand_data("Tata", expected_models)
    
    def test_mahindra_models(self):
        """Test Mahindra brand with expected models"""
        print("\n=== Testing Mahindra Car Models ===")
        expected_models = ["Scorpio N", "XUV700", "Thar", "Bolero", "XUV 3XO", "Scorpio Classic"]
        return self.test_brand_data("Mahindra", expected_models)
    
    def test_kia_models(self):
        """Test Kia brand with expected models"""
        print("\n=== Testing Kia Car Models ===")
        expected_models = ["Seltos", "Sonet", "Carens", "EV6"]
        return self.test_brand_data("Kia", expected_models)
    
    def test_invalid_brand(self):
        """Test with non-existent brand"""
        print("\n=== Testing Invalid Brand ===")
        return self.test_brand_data("InvalidBrand")
    
    def test_transmission_types_and_prices(self):
        """Test that transmission types and prices are valid"""
        print("\n=== Testing Transmission Types and Prices ===")
        
        # Test a few specific models for transmission types
        test_cases = [
            ("Tata", "Nexon", ["Manual", "AMT", "DCA"]),
            ("Mahindra", "Scorpio N", ["Manual", "Automatic"]),
            ("Kia", "Seltos", ["Manual", "Automatic"])
        ]
        
        all_passed = True
        
        for brand, model, expected_transmissions in test_cases:
            url = f"{BACKEND_URL}/car-data/{brand}"
            
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    if model in data:
                        model_data = data[model]
                        found_transmissions = set()
                        
                        for variant, transmissions in model_data.items():
                            for transmission, price in transmissions.items():
                                found_transmissions.add(transmission)
                                
                                # Validate price is in INR range (reasonable car prices)
                                if not (50000 <= price <= 10000000):  # 50k to 1 crore INR
                                    self.log_test(
                                        f"Price Validation {brand} {model}", 
                                        False, 
                                        f"Price {price} seems unrealistic for {variant}-{transmission}",
                                        {"price": price, "variant": variant, "transmission": transmission}
                                    )
                                    all_passed = False
                        
                        # Check if expected transmissions are present
                        missing_transmissions = [t for t in expected_transmissions if t not in found_transmissions]
                        if not missing_transmissions:
                            self.log_test(
                                f"Transmission Types {brand} {model}", 
                                True, 
                                f"Found expected transmission types",
                                {"found": list(found_transmissions)}
                            )
                        else:
                            self.log_test(
                                f"Transmission Types {brand} {model}", 
                                False, 
                                f"Missing transmission types: {missing_transmissions}",
                                {"expected": expected_transmissions, "found": list(found_transmissions)}
                            )
                            all_passed = False
                    else:
                        self.log_test(
                            f"Model Availability {brand} {model}", 
                            False, 
                            f"Model {model} not found in {brand} data",
                            {"available_models": list(data.keys())}
                        )
                        all_passed = False
                        
            except Exception as e:
                self.log_test(f"Transmission Test {brand} {model}", False, f"Request failed: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting MyApp Backend Car Data API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test authentication setup
        auth_success = self.test_user_registration()
        
        # Test car data endpoints
        brands_success = self.test_get_all_brands()
        tata_success = self.test_tata_models()
        mahindra_success = self.test_mahindra_models()
        kia_success = self.test_kia_models()
        invalid_success = self.test_invalid_brand()
        transmission_success = self.test_transmission_types_and_prices()
        
        # Test other brands briefly
        print("\n=== Testing Other Brands ===")
        hyundai_success = self.test_brand_data("Hyundai")
        honda_success = self.test_brand_data("Honda")
        maruti_success = self.test_brand_data("Maruti")
        volkswagen_success = self.test_brand_data("Volkswagen")
        toyota_success = self.test_brand_data("Toyota")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Overall assessment
        critical_tests = [auth_success, brands_success, tata_success, mahindra_success, kia_success]
        critical_passed = sum(critical_tests)
        
        print(f"\n🎯 CRITICAL TESTS: {critical_passed}/5 passed")
        
        if critical_passed == 5:
            print("🎉 All critical car data API tests PASSED!")
            return True
        else:
            print("⚠️  Some critical tests FAILED - needs attention")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)