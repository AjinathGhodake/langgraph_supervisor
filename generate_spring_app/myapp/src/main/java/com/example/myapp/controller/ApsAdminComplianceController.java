package com.example.myapp.controller;

import com.example.myapp.model.Character;
import com.example.myapp.service.ApsAdminComplianceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin-compliance")
public class ApsAdminComplianceController {

    @Autowired
    private ApsAdminComplianceService complianceService;

    @PostMapping("/save")
    public ResponseEntity<?> saveAdminCompliance(@RequestBody Map<String, Object> data) {
        try {
            return ResponseEntity.ok(complianceService.saveAdminCompliance(data));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}