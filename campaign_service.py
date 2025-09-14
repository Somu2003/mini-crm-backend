class CampaignService:
    def __init__(self, db):
        self.db = db
    
    def get_segment_audience(self, rules):
        return []
    
    def deliver_campaign(self, campaign_id, audience, message):
        print(f"📧 Campaign {campaign_id} delivered to {len(audience)} customers")
