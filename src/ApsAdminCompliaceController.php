<?php

namespace Ambry\PortalBundle\Controller\Aps;

use Ambry\PortalBundle\Controller\React\BaseAPSReactController;
use Ambry\PortalBundle\Entity\User\Character;
use Ambry\PortalBundle\Form\Admin\ClinicianSiteAdminType;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;

/**
 * @Route("/aps/admin-compliance")
 */
class ApsAdminCompliaceController extends BaseAPSReactController
{
    /**
     * @Route("/save", name="save_admin_compliance_clinician", options={"expose"=true}, methods={"POST"})
     */
    public function saveAdminCompliance(Request $request)
    {
        $data = $this->getRequestData($request);
        $em = $this->getDoctrine()->getManager();
        $character = $em->getRepository(Character::class)->find($data['character_id']);
        $data['version'] = $character->getVersion();
        $admin_compliance_number = $this->getParameter('compliance_agreement_number_admin');

        $form = $this->createForm(ClinicianSiteAdminType::class, $character, ['allow_extra_fields' => true, 'csrf_protection' => false]);
        $handler = $this->getFormHandler('base');
        $form->submit($data);
        if ($handler->process($form)) {
            $character->setSiteAdminComplianceAgreement($admin_compliance_number);
            $em->persist($character);
            $em->flush();
            if ($data['is_preferred_org_save']) {
                $this->get('ambry_portal.aps_my_contact_manager')->savePreferredOrganization($character);
            }
            return $this->response($character->getOrganization()->getId(), JsonResponse::HTTP_OK, $this->getSerializationGroups());
        } else {
            return $this->response($form->getErrors(), JsonResponse::HTTP_BAD_REQUEST);
        }
    }
}