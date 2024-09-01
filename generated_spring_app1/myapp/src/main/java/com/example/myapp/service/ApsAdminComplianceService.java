package com.example.myapp.service;

import com.example.myapp.model.Character;
import com.example.myapp.repository.CharacterRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class ApsAdminComplianceService {

    @Autowired
    private CharacterRepository characterRepository;

    public String saveAdminCompliance(Map<String, Object> data) {
        Long characterId = Long.valueOf(data.get("character_id").toString());
        Character character = characterRepository.findById(characterId).orElseThrow(() -> new RuntimeException("Character not found"));
        character.setVersion(data.get("version").toString());
        character.setSiteAdminComplianceAgreement("compliance_agreement_number_admin");

        characterRepository.save(character);

        if (Boolean.TRUE.equals(data.get("is_preferred_org_save"))) {
            // Save preferred organization logic
        }

        return "Compliance saved successfully";
    }
}