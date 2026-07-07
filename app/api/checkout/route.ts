import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";

export async function POST(req: NextRequest) {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  if (!secretKey) {
    return NextResponse.json(
      { error: "Stripe is not configured on the server yet." },
      { status: 500 }
    );
  }

  const { email } = await req.json();
  if (!email || typeof email !== "string") {
    return NextResponse.json({ error: "Email is required." }, { status: 400 });
  }

  const stripe = new Stripe(secretKey);
  const origin = req.headers.get("origin") || "http://localhost:3100";

  try {
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      customer_email: email,
      line_items: [
        {
          price_data: {
            currency: "aud",
            unit_amount: 1699, // AUD $16.99 founding-member early-bird reservation price
            product_data: {
              name: "SYDAR AI — Founding Member Reservation",
              description:
                "Early-bird price to reserve a founding spot (250 cap) and lock in 50% off for life. Fully refundable any time before launch.",
            },
          },
          quantity: 1,
        },
      ],
      success_url: `${origin}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/?checkout=cancelled`,
    });

    return NextResponse.json({ url: session.url });
  } catch (err) {
    return NextResponse.json(
      { error: (err as Error).message },
      { status: 502 }
    );
  }
}
