import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { toast } from 'sonner';
import { ArrowLeft, Plus, Users, TrendingUp, DollarSign } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const AdminDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [lockedGroups, setLockedGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showOfferModal, setShowOfferModal] = useState(false);
  const [offerForm, setOfferForm] = useState({
    dealer_name: '',
    price: '',
    delivery_time: '',
    bonus_items: ''
  });
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLockedGroups();
  }, []);

  const fetchLockedGroups = async () => {
    try {
      const response = await axios.get(`${API}/admin/locked-groups`);
      setLockedGroups(response.data);
    } catch (error) {
      toast.error('Failed to load locked groups');
    }
  };

  const fetchAnalytics = async (groupId) => {
    try {
      const response = await axios.get(`${API}/admin/groups/${groupId}/analytics`);
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
    }
  };

  const handleAddOffer = (group) => {
    setSelectedGroup(group);
    setShowOfferModal(true);
  };

  const handleSubmitOffer = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/admin/groups/${selectedGroup.id}/offers`, {
        dealer_name: offerForm.dealer_name,
        price: parseFloat(offerForm.price),
        delivery_time: offerForm.delivery_time,
        bonus_items: offerForm.bonus_items
      });

      toast.success('Dealer offer added successfully!');
      setShowOfferModal(false);
      setOfferForm({ dealer_name: '', price: '', delivery_time: '', bonus_items: '' });
      fetchLockedGroups();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add offer');
    } finally {
      setLoading(false);
    }
  };

  const handleViewAnalytics = (group) => {
    setSelectedGroup(group);
    fetchAnalytics(group.id);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage locked groups and dealer offers</p>
            </div>
            <Button variant="outline" onClick={() => navigate('/')} data-testid="back-to-home-admin-btn">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Locked Groups</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{lockedGroups.length}</div>
              <p className="text-xs text-muted-foreground">Ready for negotiation</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Members</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {lockedGroups.reduce((sum, g) => sum + g.current_members, 0)}
              </div>
              <p className="text-xs text-muted-foreground">Across all locked groups</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Negotiation Status</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {lockedGroups.filter(g => g.status === 'negotiation').length}
              </div>
              <p className="text-xs text-muted-foreground">Active negotiations</p>
            </CardContent>
          </Card>
        </div>

        {/* Locked Groups Table */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Locked Groups</h2>
            <p className="text-gray-600 text-sm mt-1">Groups that have reached maximum capacity</p>
          </div>

          {lockedGroups.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              No locked groups available
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Car Model
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      City
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Members
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {lockedGroups.map((group) => (
                    <tr key={group.id} data-testid={`admin-group-${group.id}`}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{group.car_model}</div>
                            <div className="text-sm text-gray-500">{group.brand}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {group.city}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {group.current_members} / {group.max_members}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`status-badge status-${group.status}`}>
                          {group.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <Button
                          size="sm"
                          onClick={() => handleAddOffer(group)}
                          data-testid={`add-offer-${group.id}-btn`}
                        >
                          <Plus className="w-4 h-4 mr-1" />
                          Add Offer
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleViewAnalytics(group)}
                          data-testid={`view-analytics-${group.id}-btn`}
                        >
                          View Analytics
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Analytics Section */}
        {analytics && (
          <div className="mt-8 bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Group Analytics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">
                  {analytics.group.car_model} - {analytics.group.city}
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Members:</span>
                    <span className="font-semibold">{analytics.members_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Votes:</span>
                    <span className="font-semibold">{analytics.total_votes}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Offers:</span>
                    <span className="font-semibold">{analytics.offers.length}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Offers</h3>
                <div className="space-y-2">
                  {analytics.offers.map((offer) => (
                    <div key={offer.id} className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-700">{offer.dealer_name}</span>
                      <div className="text-right">
                        <div className="font-semibold text-[#0B5FFF]">
                          ₹{offer.price.toLocaleString('en-IN')}
                        </div>
                        <div className="text-xs text-gray-500">{offer.votes} votes</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Add Offer Modal */}
      <Dialog open={showOfferModal} onOpenChange={setShowOfferModal}>
        <DialogContent data-testid="add-offer-modal">
          <DialogHeader>
            <DialogTitle>Add Dealer Offer</DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmitOffer} className="space-y-4">
            <div>
              <Label htmlFor="dealer_name">Dealer Name</Label>
              <Input
                id="dealer_name"
                data-testid="dealer-name-input"
                value={offerForm.dealer_name}
                onChange={(e) => setOfferForm({ ...offerForm, dealer_name: e.target.value })}
                required
              />
            </div>

            <div>
              <Label htmlFor="price">Price (₹)</Label>
              <Input
                id="price"
                data-testid="price-input"
                type="number"
                value={offerForm.price}
                onChange={(e) => setOfferForm({ ...offerForm, price: e.target.value })}
                required
              />
            </div>

            <div>
              <Label htmlFor="delivery_time">Delivery Time</Label>
              <Input
                id="delivery_time"
                data-testid="delivery-time-input"
                value={offerForm.delivery_time}
                onChange={(e) => setOfferForm({ ...offerForm, delivery_time: e.target.value })}
                placeholder="e.g., 2-3 weeks"
                required
              />
            </div>

            <div>
              <Label htmlFor="bonus_items">Bonus Items</Label>
              <Textarea
                id="bonus_items"
                data-testid="bonus-items-input"
                value={offerForm.bonus_items}
                onChange={(e) => setOfferForm({ ...offerForm, bonus_items: e.target.value })}
                placeholder="e.g., Free accessories, extended warranty"
                required
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading} data-testid="submit-offer-btn">
              {loading ? 'Adding...' : 'Add Offer'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminDashboard;