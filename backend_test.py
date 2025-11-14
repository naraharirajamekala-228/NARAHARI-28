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
    
    def test_clear_existing_groups(self):
        """Test clearing existing groups (if possible)"""
        print("\n=== Testing Clear Existing Groups ===")
        
        # First check if there are existing groups
        url = f"{BACKEND_URL}/groups"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                existing_count = len(data) if isinstance(data, list) else 0
                
                self.log_test(
                    "Check Existing Groups", 
                    True, 
                    f"Found {existing_count} existing groups",
                    {"existing_groups": existing_count}
                )
                
                # Note: We don't actually clear groups as there's no delete endpoint
                # This is just to check the current state
                return True
            else:
                self.log_test("Check Existing Groups", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("Check Existing Groups", False, f"Request failed: {str(e)}")
            return False
    
    def test_seed_data(self):
        """Test POST /api/seed-data - Seed all state groups"""
        print("\n=== Testing Seed Data Endpoint ===")
        
        url = f"{BACKEND_URL}/seed-data"
        
        try:
            response = self.session.post(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["message", "total_states", "total_brands", "total_groups_created"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Seed Data Response Structure", 
                        False, 
                        f"Missing required fields: {missing_fields}",
                        {"response": data}
                    )
                    return False
                
                # Verify expected counts
                expected_states = 36  # All Indian states and UTs
                expected_brands = 8   # Tata, Mahindra, Kia, Hyundai, Honda, Maruti, Volkswagen, Toyota
                expected_total_groups = expected_states * expected_brands  # 288
                
                if (data["total_states"] == expected_states and 
                    data["total_brands"] == expected_brands and 
                    data["total_groups_created"] == expected_total_groups):
                    
                    self.log_test(
                        "Seed Data", 
                        True, 
                        f"Successfully seeded {data['total_groups_created']} groups ({data['total_states']} states × {data['total_brands']} brands)",
                        {
                            "states": data["total_states"],
                            "brands": data["total_brands"], 
                            "total_groups": data["total_groups_created"]
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Seed Data", 
                        False, 
                        f"Incorrect counts - Expected: {expected_total_groups} groups ({expected_states} states × {expected_brands} brands)",
                        {
                            "expected": {"states": expected_states, "brands": expected_brands, "total": expected_total_groups},
                            "actual": {"states": data["total_states"], "brands": data["total_brands"], "total": data["total_groups_created"]}
                        }
                    )
                    return False
            else:
                self.log_test("Seed Data", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("Seed Data", False, f"Request failed: {str(e)}")
            return False
    
    def test_groups_by_city(self, city: str, expected_brands: List[str] = None):
        """Test GET /api/groups?city={city} - Get groups for specific city"""
        url = f"{BACKEND_URL}/groups"
        params = {"city": city}
        
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    # Check if we have 8 groups (one for each brand)
                    if len(data) == 8:
                        # Verify each group has correct structure
                        brands_found = []
                        valid_groups = True
                        validation_errors = []
                        
                        for group in data:
                            # Check required fields
                            required_fields = ["brand", "city", "current_members", "max_members"]
                            missing_fields = [field for field in required_fields if field not in group]
                            
                            if missing_fields:
                                validation_errors.append(f"Group missing fields: {missing_fields}")
                                valid_groups = False
                                continue
                            
                            # Verify city matches
                            if group["city"] != city:
                                validation_errors.append(f"Group city '{group['city']}' doesn't match requested '{city}'")
                                valid_groups = False
                            
                            # Verify member counts
                            if not (15 <= group["current_members"] <= 48):
                                validation_errors.append(f"Group {group['brand']} has invalid current_members: {group['current_members']} (should be 15-48)")
                                valid_groups = False
                            
                            if group["max_members"] != 50:
                                validation_errors.append(f"Group {group['brand']} has invalid max_members: {group['max_members']} (should be 50)")
                                valid_groups = False
                            
                            brands_found.append(group["brand"])
                        
                        # Check if all expected brands are present
                        if expected_brands:
                            missing_brands = [brand for brand in expected_brands if brand not in brands_found]
                            extra_brands = [brand for brand in brands_found if brand not in expected_brands]
                            
                            if missing_brands or extra_brands:
                                validation_errors.append(f"Brand mismatch - Missing: {missing_brands}, Extra: {extra_brands}")
                                valid_groups = False
                        
                        if valid_groups:
                            self.log_test(
                                f"Groups for {city}", 
                                True, 
                                f"Successfully retrieved 8 groups with valid structure",
                                {
                                    "city": city,
                                    "groups_count": len(data),
                                    "brands": brands_found,
                                    "member_counts": [g["current_members"] for g in data]
                                }
                            )
                            return True
                        else:
                            self.log_test(
                                f"Groups for {city}", 
                                False, 
                                f"Groups validation failed",
                                {"validation_errors": validation_errors}
                            )
                            return False
                    else:
                        self.log_test(
                            f"Groups for {city}", 
                            False, 
                            f"Expected 8 groups, got {len(data)}",
                            {"groups_count": len(data), "groups": [g.get("brand", "unknown") for g in data]}
                        )
                        return False
                else:
                    self.log_test(
                        f"Groups for {city}", 
                        False, 
                        "Response should be a list",
                        {"response_type": type(data), "response": data}
                    )
                    return False
            else:
                self.log_test(f"Groups for {city}", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test(f"Groups for {city}", False, f"Request failed: {str(e)}")
            return False
    
    def test_kerala_groups(self):
        """Test GET /api/groups?city=Kerala"""
        print("\n=== Testing Kerala Groups ===")
        expected_brands = ["Tata", "Mahindra", "Kia", "Hyundai", "Honda", "Maruti", "Volkswagen", "Toyota"]
        return self.test_groups_by_city("Kerala", expected_brands)
    
    def test_tamil_nadu_groups(self):
        """Test GET /api/groups?city=Tamil Nadu"""
        print("\n=== Testing Tamil Nadu Groups ===")
        expected_brands = ["Tata", "Mahindra", "Kia", "Hyundai", "Honda", "Maruti", "Volkswagen", "Toyota"]
        return self.test_groups_by_city("Tamil Nadu", expected_brands)
    
    def test_delhi_groups(self):
        """Test GET /api/groups?city=Delhi"""
        print("\n=== Testing Delhi Groups ===")
        expected_brands = ["Tata", "Mahindra", "Kia", "Hyundai", "Honda", "Maruti", "Volkswagen", "Toyota"]
        return self.test_groups_by_city("Delhi", expected_brands)
    
    def test_verify_total_groups_count(self):
        """Verify total groups count after seeding"""
        print("\n=== Verifying Total Groups Count ===")
        
        url = f"{BACKEND_URL}/groups"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    total_groups = len(data)
                    expected_total = 288  # 36 states × 8 brands
                    
                    if total_groups == expected_total:
                        self.log_test(
                            "Total Groups Count", 
                            True, 
                            f"Correct total groups count: {total_groups}",
                            {"total_groups": total_groups, "expected": expected_total}
                        )
                        return True
                    else:
                        self.log_test(
                            "Total Groups Count", 
                            False, 
                            f"Incorrect total groups count: {total_groups} (expected {expected_total})",
                            {"total_groups": total_groups, "expected": expected_total}
                        )
                        return False
                else:
                    self.log_test(
                        "Total Groups Count", 
                        False, 
                        "Response should be a list",
                        {"response_type": type(data)}
                    )
                    return False
            else:
                self.log_test("Total Groups Count", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_test("Total Groups Count", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting MyApp Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test authentication setup
        auth_success = self.test_user_registration()
        
        # Test seeding functionality (NEW TESTS)
        print("\n" + "=" * 60)
        print("🌱 SEED DATA TESTING")
        print("=" * 60)
        
        clear_success = self.test_clear_existing_groups()
        seed_success = self.test_seed_data()
        total_count_success = self.test_verify_total_groups_count()
        kerala_success = self.test_kerala_groups()
        tamil_nadu_success = self.test_tamil_nadu_groups()
        delhi_success = self.test_delhi_groups()
        
        # Test car data endpoints (EXISTING TESTS)
        print("\n" + "=" * 60)
        print("🚗 CAR DATA TESTING")
        print("=" * 60)
        
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
        
        # Overall assessment - Updated to include seeding tests
        seed_tests = [seed_success, total_count_success, kerala_success, tamil_nadu_success, delhi_success]
        car_data_tests = [auth_success, brands_success, tata_success, mahindra_success, kia_success]
        
        seed_passed = sum(seed_tests)
        car_data_passed = sum(car_data_tests)
        
        print(f"\n🌱 SEED DATA TESTS: {seed_passed}/5 passed")
        print(f"🚗 CAR DATA TESTS: {car_data_passed}/5 passed")
        
        if seed_passed == 5 and car_data_passed == 5:
            print("🎉 All critical tests PASSED!")
            return True
        else:
            print("⚠️  Some critical tests FAILED - needs attention")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)