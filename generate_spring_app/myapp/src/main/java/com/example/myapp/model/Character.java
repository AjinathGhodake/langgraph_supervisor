package com.example.myapp.model;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;

@Entity
public class Character {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Integer version;
    private String siteAdminComplianceAgreement;

    // Getters and setters

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
    }

    public String getSiteAdminComplianceAgreement() {
        return siteAdminComplianceAgreement;
    }

    public void setSiteAdminComplianceAgreement(String siteAdminComplianceAgreement) {
        this.siteAdminComplianceAgreement = siteAdminComplianceAgreement;
    }
}